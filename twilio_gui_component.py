import tkinter as tk
from tkinter import messagebox
import configparser
import os

class TwilioGUI:
    def __init__(self, root, make_call_function=None):
        """
        Initialize the Twilio GUI component.
        
        Args:
            root: The tkinter root window
            make_call_function: Optional function to call when making a call.
                                Should accept a message parameter.
        """
        self.root = root
        self.make_call_function = make_call_function
        self.root.title("Twilio Call Manager")
        self.root.geometry("550x500")
        self.root.resizable(False, False)
        
        # Create main frame
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Twilio Call Manager", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)
        
        # Credentials section
        cred_label = tk.Label(main_frame, text="Twilio Credentials", font=("Arial", 12, "bold"))
        cred_label.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        
        # Account SID
        sid_label = tk.Label(main_frame, text="Account SID:")
        sid_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.sid_entry = tk.Entry(main_frame, width=50)
        self.sid_entry.grid(row=2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Auth Token
        token_label = tk.Label(main_frame, text="Auth Token:")
        token_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.token_entry = tk.Entry(main_frame, width=50)
        self.token_entry.grid(row=3, column=1, sticky=tk.W, padx=(10, 0))
        
        # Phone Numbers section
        phone_label = tk.Label(main_frame, text="Phone Numbers", font=("Arial", 12, "bold"))
        phone_label.grid(row=4, column=0, columnspan=2, pady=(20, 10), sticky=tk.W)
        
        # Your Phone
        your_phone_label = tk.Label(main_frame, text="Your Phone Number:")
        your_phone_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        self.your_phone_entry = tk.Entry(main_frame, width=50)
        self.your_phone_entry.grid(row=5, column=1, sticky=tk.W, padx=(10, 0))
        format_label1 = tk.Label(main_frame, text="Format: +1XXXXXXXXXX (include country code)")
        format_label1.grid(row=6, column=1, sticky=tk.W, padx=(10, 0))
        
        # Twilio Phone
        twilio_phone_label = tk.Label(main_frame, text="Twilio Phone Number:")
        twilio_phone_label.grid(row=7, column=0, sticky=tk.W, pady=5)
        self.twilio_phone_entry = tk.Entry(main_frame, width=50)
        self.twilio_phone_entry.grid(row=7, column=1, sticky=tk.W, padx=(10, 0))
        format_label2 = tk.Label(main_frame, text="Format: +1XXXXXXXXXX (include country code)")
        format_label2.grid(row=8, column=1, sticky=tk.W, padx=(10, 0))
        
        # Message section
        message_label = tk.Label(main_frame, text="Call Message", font=("Arial", 12, "bold"))
        message_label.grid(row=9, column=0, columnspan=2, pady=(20, 10), sticky=tk.W)
        
        # Custom Message
        self.message_text = tk.Text(main_frame, width=50, height=5)
        self.message_text.grid(row=10, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.message_text.insert(tk.END, "Hey, this is your local nigerian prince, I require $100 of your support please.")
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=2, pady=(20, 0))
        
        save_btn = tk.Button(button_frame, text="Save Credentials", command=self.save_credentials)
        save_btn.grid(row=0, column=0, padx=10)
        
        call_btn = tk.Button(button_frame, text="Make Call", command=self.make_call)
        call_btn.grid(row=0, column=1, padx=10)
        
        # Status label
        self.status_label = tk.Label(main_frame, text="", fg="blue")
        self.status_label.grid(row=12, column=0, columnspan=2, pady=(20, 0))
        
        # Load existing configuration if available
        self.load_config()
    
    def load_config(self):
        """Load existing configuration if available"""
        if os.path.exists('twilio_config.ignore'):
            config = configparser.ConfigParser()
            config.read('twilio_config.ignore')
            
            try:
                # Set credentials
                if 'credentials' in config:
                    self.sid_entry.delete(0, tk.END)
                    self.sid_entry.insert(0, config['credentials'].get('account_sid', ''))
                    
                    self.token_entry.delete(0, tk.END)
                    self.token_entry.insert(0, config['credentials'].get('auth_token', ''))
                
                # Set phone numbers
                if 'phone_numbers' in config:
                    self.your_phone_entry.delete(0, tk.END)
                    self.your_phone_entry.insert(0, config['phone_numbers'].get('my_phone', ''))
                    
                    self.twilio_phone_entry.delete(0, tk.END)
                    self.twilio_phone_entry.insert(0, config['phone_numbers'].get('twilio_phone', ''))
                
                self.status_label.config(text="Configuration loaded successfully", fg="green")
            except Exception as e:
                self.status_label.config(text=f"Failed to load configuration: {e}", fg="red")
    
    def save_credentials(self):
        """Save credentials to the configuration file"""
        # Verify input
        if not self.validate_input():
            return False
        
        # Create config object
        config = configparser.ConfigParser()
        
        # Add credentials section
        config['credentials'] = {
            'account_sid': self.sid_entry.get().strip(),
            'auth_token': self.token_entry.get().strip()
        }
        
        # Add phone numbers section
        config['phone_numbers'] = {
            'my_phone': self.your_phone_entry.get().strip(),
            'twilio_phone': self.twilio_phone_entry.get().strip()
        }
        
        # Write to file
        try:
            with open('twilio_config.ignore', 'w') as configfile:
                config.write(configfile)
            self.status_label.config(text="Credentials saved successfully!", fg="green")
            return True
        except Exception as e:
            self.status_label.config(text=f"Failed to save configuration: {e}", fg="red")
            return False
    
    def validate_input(self):
        """Validate user input"""
        # Check for empty fields
        if not self.sid_entry.get().strip():
            messagebox.showerror("Validation Error", "Account SID cannot be empty!")
            return False
        
        if not self.token_entry.get().strip():
            messagebox.showerror("Validation Error", "Auth Token cannot be empty!")
            return False
        
        if not self.your_phone_entry.get().strip():
            messagebox.showerror("Validation Error", "Your Phone Number cannot be empty!")
            return False
        
        if not self.twilio_phone_entry.get().strip():
            messagebox.showerror("Validation Error", "Twilio Phone Number cannot be empty!")
            return False
        
        # Validate phone number format
        your_phone = self.your_phone_entry.get().strip()
        twilio_phone = self.twilio_phone_entry.get().strip()
        
        if not your_phone.startswith('+'):
            messagebox.showerror("Validation Error", "Your Phone Number must start with '+' and include country code!")
            return False
        
        if not twilio_phone.startswith('+'):
            messagebox.showerror("Validation Error", "Twilio Phone Number must start with '+' and include country code!")
            return False
        
        return True
    
    def make_call(self):
        """Save credentials and make a call"""
        # First save the credentials
        if not self.save_credentials():
            return
        
        # Get the message
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Message cannot be empty!")
            return
        
        # Check if make_call_function is provided
        if self.make_call_function is None:
            self.status_label.config(text="No call function provided to the GUI component", fg="red")
            messagebox.showwarning("Not Implemented", "Call functionality is not connected to this GUI")
            return
        
        # Make the call
        try:
            self.status_label.config(text="Initiating call...", fg="blue")
            self.root.update()  # Update the GUI to show the status
            
            result = self.make_call_function(message)
            if result:
                self.status_label.config(text="Call initiated successfully!", fg="green")
                messagebox.showinfo("Success", "Call initiated successfully!")
            else:
                self.status_label.config(text="Failed to make call. Check console for details.", fg="red")
                messagebox.showerror("Error", "Failed to make call. Check console for details.")
        except Exception as e:
            self.status_label.config(text=f"An error occurred: {e}", fg="red")
            messagebox.showerror("Error", f"An error occurred: {e}")

# This will only run if the file is executed directly (not imported)
if __name__ == "__main__":
    # Demo mode - just show the GUI without actual call functionality
    root = tk.Tk()
    app = TwilioGUI(root, make_call_function=lambda msg: messagebox.showinfo("Demo", f"Would call with message: {msg}"))
    root.mainloop()