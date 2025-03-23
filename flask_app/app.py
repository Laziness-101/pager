import sys
import os
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()

import openai
import pyaudio
import wave
import time
import threading
from flask import Flask, render_template, request, redirect, url_for, jsonify

from Components.call_component import make_phone_call
from Components.gemini_component import prompt_gemini

########################
# CONFIG
########################
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5

# Initialize PyAudio
p = pyaudio.PyAudio()

# Automatically find the BlackHole device index
DEVICE_INDEX = None
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if "BlackHole 2ch" in info['name']:
        DEVICE_INDEX = i
        break

# Fallback to default device if BlackHole not found
if DEVICE_INDEX is None:
    print("Warning: BlackHole 2ch device not found. Using default device.")
    DEVICE_INDEX = 2  # Keeping original default as fallback

# Shared data for wake words, phone number, logs, etc.
wake_words = ["justin", "mohammad", "data lake 2.0"]  # default
phone_number = ""
log_messages = []  # We'll store log messages here instead of SSE queue
transcription = []
stop_detection_flag = False
detection_thread = None

# API keys (will be loaded from .env if exists)
api_keys = {
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "twilio_sid": os.getenv("TWILIO_SID", ""),
    "twilio_token": os.getenv("TWILIO_TOKEN", ""),
    "twilio_phone": os.getenv("TWILIO_PHONE", ""),
    "gemini_api_key": os.getenv("GEMINI_API_KEY", "")
}

########################
# HELPER FUNCTIONS
########################
def log_message(msg: str):
    """
    Append a new log message to our global list.
    You could also limit the size here if needed.
    """
    print(msg)  # Also print to console
    log_messages.append(msg)

def record_audio(filename="temp.wav"):
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=DEVICE_INDEX)

    frames = []
    for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()

    # Save to WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return filename

def transcribe(file_path):
    print("📡 Sending to OpenAI Whisper API...")
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
        )
    return transcript.text

def save_env_file(api_keys_dict):
    """
    Save API keys to a .env file in the specified format
    """
    # Get the parent directory where app.py is located
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create .env file with the specified format
    env_path = os.path.join(app_dir, ".env")
    
    with open(env_path, "w") as f:
        f.write(f"OPENAI_API_KEY={api_keys_dict['openai_api_key']}\n")
        f.write(f"TWILIO_SID={api_keys_dict['twilio_sid']}\n")
        f.write(f"TWILIO_TOKEN={api_keys_dict['twilio_token']}\n")
        f.write(f"TWILIO_PHONE={api_keys_dict['twilio_phone']}\n")
        f.write(f"GEMINI_API_KEY={api_keys_dict['gemini_api_key']}\n")
    
    return env_path

########################
# DETECTION LOOP
########################
def detection_loop():
    """
    Continuously record, transcribe, and check for wake words.
    Logs are written to the global list.
    """
    global api_keys
    log_message("Detection started. Listening for wake words...")

    while not stop_detection_flag:
        try:
            audio_path = record_audio()
            text = transcribe(audio_path).lower().strip()
            transcription.append(text)
            log_message(f"Transcription: {text}")

            # Check each wake word
            for word in wake_words:
                if word.lower() in text:
                    log_message(f"Wake word '{word}' detected!")
                    make_phone_call(
                        sid=api_keys["twilio_sid"],
                        token=api_keys["twilio_token"],
                        phone_number=phone_number,
                        twilio_phone=api_keys["twilio_phone"],
                    )
                    log_message(f"  -- Phone call sent to {phone_number} --")
                    transcription_string = ' '.join(transcription)
                    response = prompt_gemini(
                        prompt=f"The following is the transcript of a meeting going on. The main user has been called on in the meeting and requires an urgent summarization of everything discussed. Generate a summary of everything discussed in the meeting. Transcription: ```{transcription_string}```",
                        api_key=api_keys["gemini_api_key"],
                    )
                    log_message(f"  -- Gemini response: {response} --")

        except Exception as e:
            log_message(f"Error: {e}")
            print(e)

        time.sleep(0.5)  # Short pause before next recording

    log_message("Detection stopped.")

########################
# FLASK APP
########################
app = Flask(__name__)

@app.route("/")
def index():
    """Render the main page with a form to set phone number and wake words."""
    return render_template(
        "index.html",
        phone_number=phone_number,
        wake_words=", ".join(wake_words),
        openai_api_key=api_keys["openai_api_key"],
        twilio_sid=api_keys["twilio_sid"],
        twilio_token=api_keys["twilio_token"],
        twilio_phone=api_keys["twilio_phone"],
        gemini_api_key=api_keys["gemini_api_key"]
    )

@app.route("/save_api_keys", methods=["POST"])
def save_api_keys():
    """
    Endpoint to save API keys to a .env file in the specified format,
    then redirect back to home.
    """
    global api_keys
    
    # Update API keys from form data
    api_keys["openai_api_key"] = request.form.get("openai_api_key", "")
    api_keys["twilio_sid"] = request.form.get("twilio_sid", "")
    api_keys["twilio_token"] = request.form.get("twilio_token", "")
    api_keys["twilio_phone"] = request.form.get("twilio_phone", "")
    api_keys["gemini_api_key"] = request.form.get("gemini_api_key", "")
    
    # Save to .env file
    env_path = save_env_file(api_keys)
    
    # Update the client with the new API key
    client = openai.OpenAI(api_key=api_keys["openai_api_key"])
    
    log_message(f"API keys saved to .env file at {env_path}")
    
    return redirect(url_for("index"))

@app.route("/update_settings", methods=["POST"])
def update_settings():
    """
    Endpoint to update phone number and wake words from the user form,
    then redirect back to home.
    """
    global phone_number, wake_words
    phone_number = request.form.get("phone_number", "")
    words = request.form.get("wake_words", "")
    wake_words = [w.strip() for w in words.split(",") if w.strip()]
    return redirect(url_for("index"))

@app.route("/start_detection", methods=["POST"])
def start_detection():
    """Start the background detection thread if not running."""
    global detection_thread, stop_detection_flag
    if detection_thread is None or not detection_thread.is_alive():
        stop_detection_flag = False
        detection_thread = threading.Thread(target=detection_loop, daemon=True)
        detection_thread.start()
        log_message("Detection thread started.")
    return ("", 204)

@app.route("/stop_detection", methods=["POST"])
def stop_detection():
    """Signal the detection loop to stop."""
    global stop_detection_flag
    stop_detection_flag = True
    log_message("Stopping detection thread...")
    return ("", 204)

@app.route("/logs", methods=["GET"])
def get_logs():
    """
    Return current log messages as JSON.
    The front-end polls this endpoint to display logs.
    """
    return jsonify(log_messages)

if __name__ == "__main__":
    try:
        # Log which audio device we're using
        device_info = p.get_device_info_by_index(DEVICE_INDEX)
        log_message(f"Using audio device: {device_info['name']} (index {DEVICE_INDEX})")
        
        # Try to run on port 5000, but if unavailable, use 8080 instead
        try:
            log_message("Starting server on port 5000...")
            app.run(port=5000)
        except OSError as e:
            if "Address already in use" in str(e):
                log_message("Port 5000 is in use. Switching to port 8080...")
                app.run(port=8080)
            else:
                raise
    finally:
        p.terminate()