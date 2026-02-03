import os
import google.generativeai as genai

# Paste your API key here
os.environ["GEMINI_API_KEY"] = "AIzaSyCG889QdHUJnLD5XVE0Gu-XQSo7N0AKrnk" 
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

print("Checking available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")