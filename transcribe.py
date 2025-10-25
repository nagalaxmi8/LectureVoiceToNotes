import torch
from pathlib import Path
from faster_whisper import WhisperModel

# Automatically detect GPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"  # CPU-friendly int8

MODEL_SIZE = "small"  # You can change to tiny/base/small/medium/large
MODEL = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

def transcribe_audio(audio_path: Path, language: str = "en") -> str:
    """
    Transcribe a single audio file to text.
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    segments, _ = MODEL.transcribe(str(audio_path), language=language)
    transcript = " ".join([segment.text for segment in segments])
    return transcript
