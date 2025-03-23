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
DEVICE_INDEX = 0  # BlackHole device index

# Shared data for wake words, phone number, logs, etc.
wake_words = ["justin", "mohammad", "data lake 2.0"]  # default
phone_number = ""
log_messages = []  # We'll store log messages here instead of SSE queue
transcription = []
stop_detection_flag = False
detection_thread = None

# Initialize PyAudio
p = pyaudio.PyAudio()

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

########################
# DETECTION LOOP
########################
def detection_loop():
    """
    Continuously record, transcribe, and check for wake words.
    Logs are written to the global list.
    """
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
                        sid=os.getenv("TWILIO_SID"),
                        token=os.getenv("TWILIO_TOKEN"),
                        phone_number=phone_number,
                        twilio_phone=os.getenv("TWILIO_PHONE"),
                    )
                    log_message(f"  -- Phone call sent to {phone_number} --")
                    transcription_string = ' '.join(transcription)
                    response = prompt_gemini(
                        prompt=f"The following is the transcript of a meeting going on. The main user has been called on in the meeting and requires an urgent summarization of everything discussed. Generate a summary of everything discussed in the meeting. Transcription: ```{transcription_string}```",
                        api_key=os.getenv("GEMINI_API_KEY"),
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
        wake_words=", ".join(wake_words)
    )

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
        app.run(port=5000)
    finally:
        p.terminate()