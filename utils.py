from pathlib import Path
import tempfile

def save_temp_file(uploaded_file):
    suffix = Path(uploaded_file.name).suffix
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(uploaded_file.read())
    temp_file_path = Path(temp_file.name)
    temp_file.close()
    return temp_file_path, suffix

def get_history_folder():
    folder = Path("LectureHistory")
    folder.mkdir(exist_ok=True)
    return folder

def save_lecture_history(filename: str, content: str):
    folder = get_history_folder()
    file_path = folder / filename
    file_path.write_text(content, encoding="utf-8")
    return file_path
