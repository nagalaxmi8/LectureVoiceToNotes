import google.generativeai as genai


def generate_summary(transcript: str, language: str = "English", summary_type: str = "Short") -> str:
    """
    Generate a summary using Gemini API.
    """
    prompt = f"""
    Summarize the following lecture transcript in {language} in a {summary_type.lower()} summary:

    {transcript}
    """

    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip() if response and response.text else "⚠️ No summary generated."
    except Exception as e:
        return f"⚠️ Summary generation failed: {e}\n\nPartial content:\n{transcript[:1000]}..."
