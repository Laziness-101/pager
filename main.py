import tkinter as tk
import make_call_component as caller
from twilio_gui_component import TwilioGUI

def main():
    """
    Main application entry point.
    Creates the GUI and connects it to the Twilio calling functionality.
    """
    root = tk.Tk()
    
    # Create the GUI and pass in the calling function
    app = TwilioGUI(root, make_call_function=caller.make_phone_call)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()