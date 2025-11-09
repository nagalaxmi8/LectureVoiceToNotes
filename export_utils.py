from pathlib import Path
from docx import Document
import markdown


# ----------------------------------------------------
# ✅ TXT EXPORT
# ----------------------------------------------------
def export_txt(file_path: Path, text: str):
    file_path.write_text(text, encoding="utf-8")


# ----------------------------------------------------
# ✅ DOCX EXPORT
# ----------------------------------------------------
def export_docx(file_path: Path, text: str):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(file_path)

# ----------------------------------------------------
# ✅ MARKDOWN EXPORT
# ----------------------------------------------------
def export_md(file_path: Path, text: str):
    """
    Converts text → HTML Markdown format
    """
    md_html = markdown.markdown(text)
    file_path.write_text(md_html, encoding="utf-8")
