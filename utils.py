from pathlib import Path
import tempfile

def save_temp_file(uploaded_file):
    ext = Path(uploaded_file.name).suffix
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    temp_file.write(uploaded_file.read())
    temp_file_path = Path(temp_file.name)
    temp_file.close()
    return temp_file_path
