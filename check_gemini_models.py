import os
import google.generativeai as genai

# Set your API key here (or via environment variable)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # make sure your API key is set in env
if not GEMINI_API_KEY:
    raise ValueError("❌ Set GEMINI_API_KEY in your environment variables!")

genai.configure(api_key=GEMINI_API_KEY)

# List all available models
models = genai.list_models()
print("Available Gemini models:")
for model in models:
    print("-", model)
