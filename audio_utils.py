# audio_utils.py
import subprocess
from pathlib import Path
import tempfile
from typing import List

# -------------------- Extract audio from video --------------------
def extract_audio_ffmpeg(input_file: Path, output_file: Path):
    """
    Extract audio from video or convert audio file to WAV PCM 16-bit, 44.1kHz, stereo.
    Works with MP4, MOV, MKV, WEBM, M4A, MP3.
    """
    input_file = Path(input_file)
    output_file = Path(output_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    command = [
        "ffmpeg",
        "-y",  # overwrite
        "-i", str(input_file),
        "-vn",  # no video
        "-acodec", "pcm_s16le",  # WAV PCM 16-bit
        "-ar", "44100",  # sample rate
        "-ac", "2",  # stereo
        str(output_file)
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg extraction failed:\n{e.stderr.decode()}") from e


# -------------------- Split WAV into chunks --------------------
def chunk_audio(audio_path: Path, chunk_duration_ms: int = 5*60*1000) -> List[Path]:
    """
    Split WAV audio into smaller chunks (default 5 min) for transcription.
    Returns a list of chunk file paths.
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    chunks: List[Path] = []
    chunk_duration_sec = chunk_duration_ms // 1000

    # Get total duration
    try:
        result = subprocess.run(
            ["ffprobe", "-i", str(audio_path), "-show_entries", "format=duration",
             "-v", "quiet", "-of", "csv=p=0"],
            capture_output=True, text=True, check=True
        )
        total_duration = float(result.stdout.strip())
    except Exception as e:
        raise RuntimeError(f"Failed to get audio duration with ffprobe: {e}")

    # Split into chunks
    for i, start in enumerate(range(0, int(total_duration), chunk_duration_sec)):
        temp_file = Path(tempfile.gettempdir()) / f"{audio_path.stem}_chunk{i}.wav"
        cmd = [
            "ffmpeg",
            "-y",
            "-i", str(audio_path),
            "-ss", str(start),
            "-t", str(chunk_duration_sec),
            "-acodec", "pcm_s16le",  # safe WAV format
            "-ar", "44100",
            "-ac", "2",
            str(temp_file)
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if temp_file.exists():
                chunks.append(temp_file)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Failed to create chunk {i}: {e.stderr.decode()}")

    return chunks
