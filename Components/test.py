#!/usr/bin/env python3

# Import the Gemini prompting function
from gemini_component import prompt_gemini

# Simple test with a basic prompt
def main():
    try:
        # This will automatically look for any config file in the current directory
        response = prompt_gemini("Tell me a fun fact about space.")
        
        print("\n----- Gemini Response -----")
        print(response)
        print("---------------------------\n")
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()