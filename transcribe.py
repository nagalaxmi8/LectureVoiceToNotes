from pathlib import Path
import whisper
import torch

# ----------------- Device setup -----------------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ----------------- Load Whisper model -----------------
# Available: tiny, base, small, medium, large
MODEL_SIZE = "base"
MODEL = whisper.load_model(MODEL_SIZE, device=DEVICE)

def transcribe_audio(audio_path: Path, language: str = "en") -> str:
    """
    Transcribe an audio file to text using OpenAI Whisper.
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Transcribe
    print(f"Transcribing {audio_path.name} using Whisper ({MODEL_SIZE}, {DEVICE})...")
    result = MODEL.transcribe(str(audio_path), language=language)

    # Return full text
    return result["text"].strip()
