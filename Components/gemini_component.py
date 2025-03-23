import google.generativeai as genai
import os
import json
import configparser
from pathlib import Path
from typing import Optional, List, Dict, Any

def load_api_key(config_file: Optional[str] = None) -> str:
    """
    Load API key from a configuration file.
    Supports JSON, INI, and simple text files.
    
    Args:
        config_file (str, optional): Path to the configuration file.
            If None, searches for common config files in current directory.
            
    Returns:
        str: The API key
        
    Raises:
        FileNotFoundError: If no config file is found
        ValueError: If API key cannot be parsed from config file
    """
    # Default config filenames to try
    default_files = [
        "Components/gemini_config.json", 
        "api_config.json", 
        "secrets.json",
        "config.ini", 
        "api_config.ini",
        "api_key.txt"
    ]
    
    # Use provided config file or try default ones
    if config_file:
        files_to_try = [config_file]
    else:
        files_to_try = default_files
    
    for file_name in files_to_try:
        file_path = Path(file_name)
        if not file_path.exists():
            continue
            
        # Process based on file extension
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Try common key names
                    for key in ['api_key', 'apiKey', 'google_api_key', 'gemini_api_key', 'key']:
                        if key in data:
                            return data[key]
                    # If nested under 'google', 'gemini', etc.
                    for section in ['google', 'gemini', 'api']:
                        if section in data and isinstance(data[section], dict):
                            for key in ['api_key', 'apiKey', 'key']:
                                if key in data[section]:
                                    return data[section][key]
                    
            elif suffix == '.ini':
                config = configparser.ConfigParser()
                config.read(file_path)
                # Try common sections and keys
                for section in ['api', 'google', 'gemini', 'credentials', 'DEFAULT']:
                    if section in config:
                        for key in ['api_key', 'apiKey', 'key', 'google_api_key', 'gemini_api_key']:
                            if key in config[section]:
                                return config[section][key]
                    
            else:  # Treat as plain text file with just the key
                with open(file_path, 'r') as f:
                    api_key = f.read().strip()
                    if api_key:
                        return api_key
                        
        except Exception as e:
            # Continue to the next file if there's an error
            continue
    
    # If we get here, no API key was found
    raise FileNotFoundError(
        f"No API key found. Please provide a config file or create one of: {', '.join(default_files)}"
    )

def prompt_gemini(
    prompt: str,
    config_file: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gemini-1.5-pro",
    temperature: float = 0.7,
    max_output_tokens: int = 2048,
    top_p: float = 0.95,
    top_k: int = 64,
    safety_settings: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Sends a prompt to Google Gemini API and returns the response.
    
    Args:
        prompt (str): The prompt text to send to Gemini.
        config_file (str, optional): Path to configuration file containing the API key.
        api_key (str, optional): Google API key. If None, tries to load from config_file or environment.
        model (str): Gemini model to use. Default is "gemini-1.5-pro".
        temperature (float): Controls randomness of output. Lower is more deterministic. Range: [0.0, 1.0]
        max_output_tokens (int): Maximum number of tokens in the response.
        top_p (float): Nucleus sampling parameter. Range: [0.0, 1.0]
        top_k (int): Number of highest probability tokens to consider for each step. Range: [1, 100]
        safety_settings (List[Dict[str, Any]], optional): Safety settings configuration.
        
    Returns:
        str: Text response from Gemini
        
    Raises:
        ValueError: If API key is not provided and cannot be loaded
        Exception: For API errors or connection issues
    """
    # Get API key from different sources in priority order
    if not api_key:
        try:
            # First try to load from config file
            api_key = load_api_key(config_file)
        except FileNotFoundError:
            # Fall back to environment variable
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key must be provided, set in a config file, or set as GOOGLE_API_KEY environment variable"
                )
    
    # Configure the generative AI library
    genai.configure(api_key=api_key)
    
    # Set up the model
    generation_config = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_output_tokens": max_output_tokens,
    }
    
    # Create model instance
    model = genai.GenerativeModel(
        model_name=model,
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    
    try:
        # Send the prompt and get response
        response = model.generate_content(prompt)
        
        # Return the text from the response
        return response.text
    except Exception as e:
        raise Exception(f"Error calling Gemini API: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Create a sample config.json file if you don't have one
    """
    Example config.json:
    {
        "api_key": "your_api_key_here"
    }
    
    Example config.ini:
    [api]
    api_key = your_api_key_here
    
    Example api_key.txt:
    your_api_key_here
    """
    
    try:
        # Method 1: Load from a config file automatically
        response = prompt_gemini(
            prompt="Explain quantum computing in simple terms"
            # The function will automatically search for config files
        )
        
        # Method 2: Specify a particular config file
        # response = prompt_gemini(
        #     prompt="Explain quantum computing in simple terms",
        #     config_file="path/to/your/config.json"
        # )
        
        # Method 3: Directly provide the API key
        # response = prompt_gemini(
        #     prompt="Explain quantum computing in simple terms",
        #     api_key="your_api_key_here"
        # )
        
        print(response)
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        print("Please create a config file with your API key or provide it directly.")