import google.generativeai as genai
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Missing API key! Set GEMINI_API_KEY environment variable.")

# configure once
genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "models/gemini-2.5-flash"  # ✅ this one WORKS

def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe audio using Gemini multimodal (generateContent).
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)

        response = model.generate_content(
            [
                {
                    "mime_type": "audio/*",
                    "data": audio_bytes
                },
                "Transcribe this audio clearly into text."
            ]
        )

        if response and hasattr(response, "text"):
            return response.text.strip()

        return "⚠️ No text returned from Gemini."

    except Exception as e:
        return f"⚠️ Transcription failed: {e}"
