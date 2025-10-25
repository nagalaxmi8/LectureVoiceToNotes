# generate_quiz.py
import os
import google.generativeai as genai

# Make sure your GEMINI_API_KEY is set in environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Please set GEMINI_API_KEY in your environment variables.")

def generate_quiz(transcript: str, language: str = "English", include_answers: bool = True) -> str:
    """
    Generate a 10-question multiple-choice quiz from a lecture transcript using Gemini API.
    """
    answer_text = (
        "Include correct answers at the end of each question."
        if include_answers
        else "Do not include answers."
    )

    prompt = f"""
    Create a 10-question multiple-choice quiz in {language} based on the following lecture transcript.
    Each question should have 4 options (A–D).
    {answer_text}

    Transcript:
    {transcript}
    """

    try:
        # Initialize the model — API key will be automatically read from environment
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        response = model.generate_content(prompt)
        if response and hasattr(response, "text") and response.text:
            return response.text.strip()
        else:
            return "⚠️ No quiz generated."
    except Exception as e:
        # Return partial transcript in case of failure
        return f"⚠️ Quiz generation failed: {e}\n\nPartial content:\n{transcript[:1000]}..."
