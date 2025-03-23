#!/usr/bin/env python
"""
Flask Server Launcher
---------------------
This script launches the Flask server from app.py and automatically
opens the website in your default browser.
"""
import os
import sys
import time
import threading
import webbrowser
import subprocess

def open_browser():
    """
    Wait a moment for the Flask server to start,
    then open the website in the default browser
    """
    # Short delay to let the server start up
    time.sleep(1.5)
    url = "http://127.0.0.1:5000/"
    print(f"Opening {url} in your browser...")
    webbrowser.open(url)

if __name__ == "__main__":
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to app.py (assuming it's in the same directory)
    app_path = os.path.join(script_dir, "flask_app/app.py")
    
    if not os.path.exists(app_path):
        print(f"Error: Could not find {app_path}")
        sys.exit(1)
    
    # Start a thread to open the browser after a short delay
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Print information
    print("Starting Flask server...")
    print("Press CTRL+C to stop the server")
    
    try:
        # Run the Flask app as a subprocess
        # This way, any output from app.py will be shown in the console
        subprocess.run([sys.executable, app_path], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\nServer encountered an error: {e}")