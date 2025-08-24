import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Make sure you have your Gemini API key in .env as GEMINI_API_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file!")

genai.configure(api_key=GEMINI_API_KEY)

def summarize_email(prompt, model="models/gemini-1.5-pro-latest"):
    try:
        model = genai.GenerativeModel(model)
        response = model.generate_content(prompt, stream=False)
        # "text" for gemini-pro, "candidates" for some other models
        if hasattr(response, "text") and response.text:
            return response.text
        elif hasattr(response, "candidates") and response.candidates:
            return response.candidates[0]['content']['parts']['text']
        else:
            print("[Gemini] No valid response from Gemini API.")
            return ""
    except Exception as e:
        print(f"[Gemini] Error: {e}")
        return "AI failed. Error: " + str(e)
