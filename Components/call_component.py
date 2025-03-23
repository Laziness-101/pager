from twilio.rest import Client
import configparser
import os

# os.chdir("Components")

def make_phone_call(message="Hello! You have been called by the Laziness-101", sid=None, token=None, phone_number=None, twilio_phone=None):
    # Check if config file exists
    # if not os.path.exists('Components/twilio_config.ignore'):
    #     print("Error: twilio_config.ignore file not found!")
    #     print("Please create this file with your Twilio credentials and phone numbers.")
    #     return False
    
    # Read configuration from .ignore file
    if not sid or not token or not phone_number or not twilio_phone:
        config = configparser.ConfigParser()
        config.read('Components/twilio_config.ignore')
    
    # Get credentials
    try:
        # account_sid = sid if sid else config['credentials']['account_sid']
        # auth_token = token if token else config['credentials']['auth_token']
        # my_phone = phone_number if phone_number else config['phone_numbers']['my_phone']
        # twilio_phone = twilio_phone if twilio_phone else config['phone_numbers']['twilio_phone']
        account_sid = sid
        auth_token = token
        my_phone = phone_number
        twilio_phone = twilio_phone
        
        # Check if credentials have been updated
        if account_sid == "your_account_sid_here" or auth_token == "your_auth_token_here":
            print("Error: Please update the credentials in twilio_config.ignore file!")
            return False
            
        # Check if phone numbers have been updated
        if "+1YOURNUMBER" in my_phone or "+1TWILIONUMBER" in twilio_phone:
            print("Error: Please update the phone numbers in twilio_config.ignore file!")
            return False
            
    except KeyError as e:
        print(f"Error: Missing configuration: {e}")
        return False
    
    # Initialize the Twilio client
    client = Client(account_sid, auth_token)
    
    try:
        # Create TwiML - This is the XML that tells Twilio what to say/do during the call
        twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{message}</Say>
    <Pause length="1"/>
    <Say voice="alice">Call completed. Goodbye!</Say>
</Response>'''
        
        # Make a call using the TwiML directly
        call = client.calls.create(
            to=my_phone,
            from_=twilio_phone,
            twiml=twiml  # Directly provide TwiML instead of URL
        )
        
        print(f"Call SID: {call.sid}")
        print("Call initiated successfully!")
        return True
        
    except Exception as e:
        print(f"Error making call: {e}")
        print("Detailed error information:", str(e))
        return False

if __name__ == "__main__":
    # You can customize the message here
    custom_message = "Yo mama!"
    make_phone_call(custom_message)