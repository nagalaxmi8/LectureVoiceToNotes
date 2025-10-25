from pathlib import Path
from docx import Document
from fpdf import FPDF
import markdown

# ----------------------------- TXT -----------------------------
def export_txt(file_path: Path, text: str):
    file_path.write_text(text, encoding="utf-8")

# ----------------------------- DOCX -----------------------------
def export_docx(file_path: Path, text: str):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(file_path)

# ----------------------------- PDF -----------------------------
def export_pdf(file_path: Path, text: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)
    pdf.output(file_path)

# ----------------------------- MARKDOWN -----------------------------
def export_md(file_path: Path, text: str):
    md_text = markdown.markdown(text)
    file_path.write_text(md_text, encoding="utf-8")
