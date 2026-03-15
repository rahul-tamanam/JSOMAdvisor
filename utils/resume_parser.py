import PyPDF2
import os

def parse_resume(file_path):
    """
    Takes a path to a PDF resume and returns extracted text.
    """
    if not os.path.exists(file_path):
        return None, "File not found. Please check the path and try again."

    if not file_path.lower().endswith(".pdf"):
        return None, "Only PDF files are supported. Please provide a .pdf file."

    try:
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

        if not text.strip():
            return None, "Could not extract text from this PDF. It may be scanned or image-based."

        return text.strip(), None

    except Exception as e:
        return None, f"Error reading PDF: {str(e)}"