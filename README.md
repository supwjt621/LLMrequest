# LLMrequest
make a LLM request

config.py
- This file contains API keys for various LLM services:
    - GEMINI_API_KEY: Google Gemini API key
    - THAI_LLM_KEY: ThaiLLM API key
    - TYPHOON_API_KEY: Typhoon API key
    These keys are used to authenticate requests to their respective LLM APIs.

error.html
- This is an HTML error page from Cloudflare indicating a "502: Bad gateway" error from the ThaiLLM service at thaillm.or.th. The error occurred on July 3, 2026, and suggests the backend server is temporarily unavailable.

gemini.py
- This file implements functionality to interact with Google's Gemini API:
    Imports necessary modules and sets up the API key from config
    Creates a client instance for the Gemini API
    Reads content from alteplase.md file
    Defines a comprehensive system prompt that establishes a medical practitioner persona with responsibilities including:
        Medication analysis and explanation
        Prescription review for errors
        Structured extraction of medication data from documents
        Clear distinction between potential issues and clinically significant concerns
        Avoidance of medical jargon when appropriate

thaiLLM.py
- This file implements a CLI interface for interacting with the ThaiLLM API:
    Imports required libraries and loads the ThaiLLM API key
    Sets up the API endpoint URL and authentication headers
    Implements a ContinuePrompt() function that creates an interactive loop:
    Takes user input until "Quit" is entered
    Sends requests with a specific model ("thalle-0.2-thaillm-8b-fa")
    Processes the response, extracting text after " للغا"
    Handles HTTP errors appropriately

typhoon_mdfile.py
- This file implements a basic LLM interaction system using the Typhoon API:
    Imports required libraries and loads the Typhoon API key
    Configures the API endpoint and model
    Reads content from alteplase.md file
    Sets up a system prompt establishing the Typhoon AI persona
    Creates a user message with a question based on the document content
    Makes a streaming POST request to the API
    Processes the streaming response, printing each chunk as it arrives

typhoon_requests.py
- This file implements another version of Typhoon API interaction using the requests library:
    Similar setup to typhoon