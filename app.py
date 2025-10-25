import os
import tempfile
from pathlib import Path
#from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

import streamlit as st
from yt_dlp import YoutubeDL

from audio_utils import extract_audio_ffmpeg, chunk_audio
from generate_summary import generate_summary
from generate_quiz import generate_quiz
from utils import save_temp_file
#from transcribe import transcribe_audio
import torch
from faster_whisper import WhisperModel

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="🎙️ Text-to-Talk Lectures", layout="wide")

# -------------------- LOAD CSS --------------------
def load_css(file_name):
    if Path(file_name).exists():
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles.css")

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.header("🧭 Navigation")
    st.markdown("- Upload lectures")
    st.markdown("- Generate notes or quizzes")
    st.markdown("- Download the generated Notes")
    st.markdown("---")

# -------------------- HEADING --------------------
st.markdown("<h1>🎙️ Text-to-Talk Lectures</h1>", unsafe_allow_html=True)
st.write("Upload a lecture file or provide a YouTube link to generate notes and quizzes instantly.")

# -------------------- LANGUAGE SELECTION --------------------
languages = ["English", "Hindi", "Telugu", "French", "Spanish"]
selected_lang = st.selectbox("🌍 Select Language", languages)

# -------------------- FILE UPLOAD / YOUTUBE --------------------
st.markdown("### 📂 Upload Lecture File")
col_center = st.columns([0.5, 3, 0.5])
with col_center[1]:
    uploaded_file = st.file_uploader(
        "Drag and drop your lecture file here",
        type=["mp3", "wav", "mp4", "mov", "mkv", "mpeg4"],
        help="Limit 200MB per file • Supported: MP3, WAV, MP4, MOV, MKV",
    )
    youtube_url = st.text_input("📺 Or enter YouTube video URL")

audio_temp_path = None
IS_CLOUD = "STREAMLIT_SERVER_PORT" in os.environ

# -------------------- HANDLE UPLOADED FILE --------------------
if uploaded_file:
    temp_path, suffix = save_temp_file(uploaded_file)
    if suffix.lower() in [".mp4", ".mov", ".mkv"]:
        audio_temp_path = temp_path.with_suffix(".wav")
        st.info("🔊 Extracting audio (fast with ffmpeg)...")
        extract_audio_ffmpeg(temp_path, audio_temp_path)
    else:
        audio_temp_path = temp_path

# -------------------- HANDLE YOUTUBE --------------------
elif youtube_url:
    if IS_CLOUD:
        st.warning(
            "⚠️ YouTube downloads are disabled on deployed Streamlit. "
            "Please upload a local audio file."
        )
    else:
        TEMP_YT_DIR = Path(tempfile.gettempdir()) / "YT_Temp"
        TEMP_YT_DIR.mkdir(exist_ok=True)
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "outtmpl": str(TEMP_YT_DIR / "%(title)s.%(ext)s"),
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": True,
            "socket_timeout": 30,
            "retries": 3,
        }

        try:
            with st.spinner("⏳ Downloading YouTube audio..."):
                with YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(youtube_url, download=True)
                    downloaded_file = Path(ydl.prepare_filename(info_dict))
                    
                    audio_temp_path = downloaded_file.with_suffix(".wav")
                    if not audio_temp_path.exists():
                        st.info("🔊 Converting audio to WAV for transcription...")
                        command = [
                            "ffmpeg",
                            "-y",
                            "-i", str(downloaded_file),
                            "-acodec", "pcm_s16le",
                            "-ar", "44100",
                            "-ac", "2",
                            str(audio_temp_path)
                        ]
                        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if audio_temp_path.exists():
                st.success(f"✅ YouTube audio ready: {audio_temp_path.name}")
            else:
                st.error("❌ Audio conversion to WAV failed.")
        
        except subprocess.CalledProcessError as e:
            st.error(f"❌ FFmpeg extraction failed:\n{e.stderr.decode()}")
        except Exception as e:
            st.error(f"❌ Failed to download or convert YouTube video: {e}")

# -------------------- SUMMARY TYPE --------------------
st.markdown("### 📝 Choose Summary Type")
if "summary_type" not in st.session_state:
    st.session_state.summary_type = "Short"

col_a, col_b = st.columns(2)
with col_a:
    if st.button("🩵 Short Summary"):
        st.session_state.summary_type = "Short"
with col_b:
    if st.button("💜 Detailed Summary"):
        st.session_state.summary_type = "Detailed"

st.info(f"✅ Selected Summary Type: **{st.session_state.summary_type}**")

# -------------------- TRANSCRIPTION --------------------

transcript = ""
if audio_temp_path and Path(audio_temp_path).exists():
    st.audio(str(audio_temp_path))
    st.info("🎧 Preprocessing audio for faster transcription...")

    # 1️⃣ Convert to mono + 16kHz WAV (overwrite temp)
    processed_audio = Path(tempfile.gettempdir()) / f"{audio_temp_path.stem}_mono16k.wav"
    command = [
        "ffmpeg", "-y",
        "-i", str(audio_temp_path),
        "-ac", "1",      # mono
        "-ar", "16000",  # 16kHz
        str(processed_audio)
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 2️⃣ Chunk audio (2 min chunks)
    chunks = chunk_audio(processed_audio, chunk_duration_ms=2*60*1000)

    # 3️⃣ Load faster_whisper model (GPU if available)
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "float32"
    MODEL_SIZE = "small"  # tiny/base/medium/large (smaller → faster)
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

    st.info(f"💨 Transcribing {len(chunks)} chunks on {DEVICE.upper()}...")

    # 4️⃣ Sequential chunk transcription (safe on Windows)
    transcript_parts = []
    progress_bar = st.progress(0)
    for i, chunk_path in enumerate(chunks):
        try:
            segments, info = model.transcribe(str(chunk_path))
            chunk_text = " ".join([seg.text for seg in segments])
            transcript_parts.append(chunk_text)
        except Exception as e:
            st.error(f"❌ Error transcribing chunk {chunk_path.name}: {e}")
            transcript_parts.append("")
        progress_bar.progress((i + 1) / len(chunks))

    transcript = " ".join([part for part in transcript_parts if part.strip()])
    st.success("✅ Transcription complete!")


# -------------------- VIEW TRANSCRIPT --------------------
if transcript:
    with st.expander("📜 View Transcript", expanded=False):
        st.write(transcript[:5000] + "...")

# -------------------- SUMMARY & QUIZ --------------------
col3, col4 = st.columns(2)

with col3:
    if transcript and st.button("✨ Generate Summary"):
        with st.spinner("🧠 Generating summary..."):
            summary_text = generate_summary(transcript, selected_lang, st.session_state.summary_type)
        with st.expander("📘 View Summary"):
            st.write(summary_text)
        st.download_button(
            "📥 Download Summary",
            data=summary_text,
            file_name=f"LectureSummary_{selected_lang}.txt",
            mime="text/plain",
        )

with col4:
    if transcript and st.button("📝 Generate Quiz & Answers"):
        with st.spinner("🧩 Creating quiz with answers..."):
            quiz_text = generate_quiz(transcript, selected_lang, include_answers=True)
        with st.expander("🎯 View Quiz & Answers"):
            st.write(quiz_text)
        st.download_button(
            "📥 Download Quiz",
            data=quiz_text,
            file_name=f"LectureQuiz_{selected_lang}.txt",
            mime="text/plain",
        )

# -------------------- FOOTER --------------------
st.markdown(
    """
    <hr>
    <p style='text-align:center; color:gray'>
         Powered by Local Whisper & Streamlit
    </p>
    """,
    unsafe_allow_html=True,
)
