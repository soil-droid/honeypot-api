import os
from dotenv import load_dotenv # Use the library we installed earlier
import google.generativeai as genai

# 1. Load the secret .env file (for local testing)
load_dotenv()

# 2. Get the key from the environment
api_key = os.getenv("GEMINI_API_KEY")

# Check if key exists
if not api_key:
    raise ValueError("No API Key found! Make sure GEMINI_API_KEY is set in .env or Render.")

genai.configure(api_key=api_key)

# ... rest of your code ...

# --- CONFIGURATION ---
# Get your API key from https://aistudio.google.com/


model = genai.GenerativeModel('gemini-flash-latest')# --- THE PERSONA ---
SYSTEM_PROMPT = """
You are Vikram, a 'Verification Support Officer' at the 'Central Digital Compliance Unit'. 
You are speaking to a potential scammer. Your goal is to WASTE THEIR TIME without revealing you are an AI.

Personality:
- Extremely polite but painfully bureaucratic.
- You CANNOT process their request (money, OTP, clicking links) until they provide nonsensical "verification codes" or "forms".
- Example: "Sir, I can help, but first I need the Form 27B-Slash-6 referencing your District Code."
- Feign ignorance about technology. "Is that the UPI with the blue logo or the green one?"

Objective:
1. Keep them talking as long as possible.
2. Extract their UPI ID, Phone Number, or Bank Details if they share it.
3. NEVER give them real money or credentials.
"""

def generate_honeypot_response(conversation_history):
    """
    Sends the conversation history to Gemini and gets the next bureaucratic reply.
    """
    # Format history for Gemini
    # Gemini expects: contents=[{'role': 'user', 'parts': [...]}, {'role': 'model', ...}]
    
    # We prepend the system prompt to the latest message or context
    full_prompt = SYSTEM_PROMPT + "\n\nCURRENT CONVERSATION:\n"
    
    for msg in conversation_history:
        role = "Scammer" if msg['role'] == 'user' else "Vikram"
        full_prompt += f"{role}: {msg['content']}\n"
        
    full_prompt += "Vikram: "
    
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        return f"System Error 404: Verification Service Down. {str(e)}"

# --- INTELLIGENCE EXTRACTOR (Simple Regex Version) ---
import re

def extract_intelligence(text):
    """
    Scans text for phone numbers, UPI IDs, and URLs.
    """
    intelligence = {
        "phone_numbers": re.findall(r'\b\d{10}\b', text),
        "upi_ids": re.findall(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}', text),
        "urls": re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text)
    }
    return intelligence