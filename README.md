# Documentation

## Getting Started

### Twilio Setup

#### Prerequisites
Make sure you have Twilio installed by running the command:
```
pip install twilio
```
```
pip install openai
```
Install pyaudio
```
brew install portaudio
pip install pyaudio
```
Install dotenv
```
pip install python-dotenv
```
Install google gemini api if you want gemini AI summarizer:
```
pip install google.generativeai
```
#### Getting Audio Recognition Setup

1. For **Mac Users** install the Mac Blackhole Audio Driver at this [link] (https://github.com/ExistentialAudio/BlackHole) (Make sure to download the 2ch version)
2. Open the app "Audio MIDI Setup"
3. Create a new device by clicking the bottom left "+" sign
4. Select "Macbook Pro Speakers" and "Blackhole 2ch"
5. Make sure "Drift Connection" is enabled on Blackhole 2ch
6. Now set your audio to the sound you want it to be enabled at
7. Now go to Settings -> Sound Output -> Output
8. Select the Multi-Output Device or whatever the audio connection was named on steps 4 - 5 (This should lock in your computer volume changing)

#### Getting Your Twilio Phone Number
You can get your Twilio phone number by following these steps or by watching this [YouTube Video](https://www.youtube.com/watch?v=Sqsz2T1Bzlg&t=29s).

1. Go to the [Twilio Website](https://www.twilio.com/en-us)
2. Create a new account by clicking the sign-up button in the top right corner
3. Verify your phone number through the signup process
4. Verify your email address
5. Complete the survey questions according to your preferences
6. On your account dashboard, click on "Get a Twilio phone number"
7. Scroll down to find the Account Info tab
8. Expand the tab to locate your:
   - Account SID
   - Auth Token
   - My Twilio Phone Number
9. Copy and paste these credentials into the website

![Twilio Dashboard Example](Images/AccountInfoTutorial.png)

### Possible Bugs
- Sometimes the app may crash after some uses, in these cases you may need to reset the cookies on 
- Certain old softwares with old audio drivers may not be compatible with this software such as zoom, but google meetings, discord and MS teams have proved to be consistent

## Development Docs
### Functionality Chart

```mermaid
---
title: Meetings Pager
---
graph LR
    A(Computer Audio Input) --> b(Local Transcriber)
    A --> B(OpenAI's Whisper Model)
    B -- Transcribes text--> C(Stores local transcript)
    C --> D(Keyword/Name Detection from transcript)
    D --> E(Sentence Filtering if your name is called for a good reason)
    E --> F(Returns Summary on topics of what you've talked about)
    E --> G(Calls your Phone)
    b --> c(Keyword/Name Detection from transcript)
    c --> d(Calls your Phone)
    
```

### Folders/Files
```
├── main.py                 # Main execution of the functions toether
├── docs                    # Documentation files (alternatively `doc`)
├── Components              # Components of the pager
│   ├── call_component.py   # Number Calling Functionality
│   ├── gui_component.py    # Python Gui Maker
│   ├── gemini_componenet.py# Gemini prompting AI
├── Images/                 # Miscellaneous Images
├── LICENSE                 # License to prevent people from commercializing our product
├── .gitignore              # Telling github to ignore your credentials from being uploaded
├── README.md               # This file for documentation
└── ...
```