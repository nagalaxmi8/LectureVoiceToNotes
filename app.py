# app.py
#import io
import hashlib
from pathlib import Path

import streamlit as st
import yt_dlp

# Internal modules (as you already have them)
from transcribe import transcribe_audio
from generate_summary import generate_summary
from generate_quiz import generate_quiz
from export_utils import export_docx # Unicode-safe in your version


# -----------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------
st.set_page_config(page_title="🎙️ Text-to-Talk Lectures", layout="wide")


# -----------------------------------------------------------
# LOAD CSS
# -----------------------------------------------------------
def load_css():
    css_file = Path("style.css")
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)





# -----------------------------------------------------------
# TITLE
# -----------------------------------------------------------
st.markdown("<h1>🎙️ Text-to-Talk Lectures</h1>", unsafe_allow_html=True)
st.write("Convert audio/video lectures into text, summary, and quizzes instantly.")


# -----------------------------------------------------------
# LANGUAGE SELECT
# -----------------------------------------------------------
language = st.selectbox(
    "🌍 Select Language",
    ["English", "Hindi", "Telugu", "French", "Spanish"],
    key="lang_select",
)


# -----------------------------------------------------------
# FILE UPLOAD
# -----------------------------------------------------------
st.markdown("### 📂 Upload Lecture File")
uploaded_file = st.file_uploader(
    "Drag and drop your file here",
    type=["mp3", "wav", "mp4", "m4a", "mov", "mkv"],
    help="Accepts audio/video files"
)


# -----------------------------------------------------------
# YOUTUBE INPUT
# -----------------------------------------------------------
st.markdown("### 📺 Enter YouTube URL (optional)")
youtube_url = st.text_input("Paste YouTube link", key="yt_url")


# -----------------------------------------------------------
# AUDIO BYTES PIPELINE
# -----------------------------------------------------------
audio_bytes = None

# Prefer uploaded file if present
if uploaded_file:
    audio_bytes = uploaded_file.read()
    st.success("✅ File received!")

# Else try YouTube
elif youtube_url.strip():
    st.info("⏳ Downloading YouTube audio…")
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "noplaylist": True,
            "outtmpl": "%(id)s.%(ext)s",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            downloaded_path = Path(f"{info['id']}.{info['ext']}")
        audio_bytes = downloaded_path.read_bytes()
        # best-effort cleanup
        try:
            downloaded_path.unlink(missing_ok=True)
        except Exception:
            pass
        st.success("✅ YouTube audio ready!")
    except Exception as e:
        st.error(f"❌ YouTube download failed: {e}")


# -----------------------------------------------------------
# TRANSCRIPTION (cached per-audio hash to avoid rework)
# -----------------------------------------------------------
st.markdown("### 📝 Transcript")

if audio_bytes:
    # Hash for caching (don’t re-transcribe same audio)
    audio_hash = hashlib.sha256(audio_bytes).hexdigest()
    cache_key = f"transcript::{audio_hash}"

    if cache_key in st.session_state:
        transcript = st.session_state[cache_key]
        st.info("🔁 Using cached transcript.")
    else:
        st.info("⏳ Transcribing… please wait.")
        transcript = transcribe_audio(audio_bytes)
        st.session_state[cache_key] = transcript

    if isinstance(transcript, str) and transcript.startswith("⚠️"):
        st.error(transcript)
    else:
        st.session_state["transcript_text"] = transcript
        st.success("✅ Transcription complete!")

# Show transcript
if st.session_state.get("transcript_text"):
    with st.expander("📜 View Transcript"):
        st.write(st.session_state["transcript_text"][:5000] + "…")


# -----------------------------------------------------------
# SUMMARY TYPE + GENERATE SUMMARY
# -----------------------------------------------------------
if st.session_state.get("transcript_text"):
    st.markdown("### 📝 Choose Summary Type")

    if "summary_type" not in st.session_state:
        st.session_state.summary_type = "Short"

    col_sum1, col_sum2 = st.columns(2)
    if col_sum1.button("🩵 Short Summary"):
        st.session_state.summary_type = "Short"
    if col_sum2.button("💜 Detailed Summary"):
        st.session_state.summary_type = "Detailed"

    st.info(f"✅ Selected Summary Type: **{st.session_state.summary_type}**")

    if st.button("✨ Generate Summary"):
        summary_text = generate_summary(
            st.session_state["transcript_text"],
            language,
            st.session_state["summary_type"],
        )
        st.session_state["summary_text"] = summary_text


# -----------------------------------------------------------
# SUMMARY CARD (D1: downloads inside the card)
# -----------------------------------------------------------
if st.session_state.get("summary_text"):
    st.markdown("### 📘 Summary")
    st.write(st.session_state["summary_text"])

    # Downloads row (inside the card)
    st.markdown("#### ⬇️ Download Summary")
    col_d1, col_d2, col_d3, col_d4 = st.columns(4)

    # TXT (direct)
    with col_d1:
        st.download_button(
            "📄 TXT",
            data=st.session_state["summary_text"],
            file_name="summary.txt",
            mime="text/plain",
            key="dl_sum_txt",
        )

    # DOCX (buffer via temp file)
    with col_d2:
        tmp_docx = Path("summary.docx")
        export_docx(tmp_docx, st.session_state["summary_text"])
        with open(tmp_docx, "rb") as f:
            st.download_button(
                "📘 DOCX",
                data=f.read(),
                file_name="summary.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="dl_sum_docx",
            )
        try:
            tmp_docx.unlink(missing_ok=True)
        except Exception:
            pass


    # Markdown (as .md text)
    with col_d4:
        st.download_button(
            "📝 Markdown",
            data=st.session_state["summary_text"],
            file_name="summary.md",
            mime="text/markdown",
            key="dl_sum_md",
        )


# -----------------------------------------------------------
# GENERATE QUIZ
# -----------------------------------------------------------
if st.session_state.get("transcript_text"):
    if st.button("📝 Generate Quiz"):
        quiz_text = generate_quiz(
            st.session_state["transcript_text"],
            language,
            include_answers=True,  # your function supports this flag
        )
        st.session_state["quiz_text"] = quiz_text


# -----------------------------------------------------------
# QUIZ CARD (D1: downloads inside the card)
# -----------------------------------------------------------
if st.session_state.get("quiz_text"):
    st.markdown("### 🎯 Quiz")
    st.write(st.session_state["quiz_text"])

    st.markdown("#### ⬇️ Download Quiz")
    col_q1, col_q2, col_q3 = st.columns(3)

    # TXT
    with col_q1:
        st.download_button(
            "📄 TXT",
            data=st.session_state["quiz_text"],
            file_name="quiz.txt",
            mime="text/plain",
            key="dl_quiz_txt",
        )

    # DOCX
    with col_q2:
        tmp_q_docx = Path("quiz.docx")
        export_docx(tmp_q_docx, st.session_state["quiz_text"])
        with open(tmp_q_docx, "rb") as f:
            st.download_button(
                "📘 DOCX",
                data=f.read(),
                file_name="quiz.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="dl_quiz_docx",
            )
        try:
            tmp_q_docx.unlink(missing_ok=True)
        except Exception:
            pass

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.markdown(
    "<hr><p style='text-align:center;color:gray;'>Powered by Gemini AI & Streamlit</p>",
    unsafe_allow_html=True,
)
