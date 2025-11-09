import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_quiz(transcript: str, language: str = "English", include_answers: bool = True) -> str:
    """
    Generate a quiz from the transcript using Gemini.
    include_answers = True -> Includes answer key
    include_answers = False -> Only questions
    """
    model = genai.GenerativeModel("models/gemini-pro-latest")

    prompt = f"""
    Based on the following lecture transcript, create a quiz in {language}.

    Transcript:
    {transcript}

    Requirements:
    - 10 questions
    - Mix of MCQs and short answers
    - Clear formatting

    Include answers: {include_answers}
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Quiz generation failed: {e}"
