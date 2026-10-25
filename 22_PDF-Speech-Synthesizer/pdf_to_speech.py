from gtts import gTTS
import os
import time
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        txt = page.extract_text()
        if txt:
            full_text += txt + "\n\n"
    cleaned_text = " ".join(full_text.split())
    return cleaned_text

def convert_text_to_thai_speech(text_input: str, output_path: str, slow: bool = False):
    if not text_input:
        raise ValueError("Text input is empty")
    tts = gTTS(text=text_input, lang="th", slow=slow)
    tts.save(output_path)
    return output_path

if __name__ == "__main__":
    pdf_file = "locate.pdf"
    if os.path.exists(pdf_file):
        text = extract_text_from_pdf(pdf_file)
        if text:
            convert_text_to_thai_speech(text[:200], "sample_audio.mp3")
