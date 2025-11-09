import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "models/gemini-2.5-flash"

def generate_summary(text, lang="English", summary_type="Short"):
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        prompt = f"Summarize this transcript in {lang} with a {summary_type.lower()} style:\n{text}"
        response = model.generate_content(prompt)

        return response.text.strip()
    except Exception as e:
        return f"⚠️ Summary generation failed: {e}"
