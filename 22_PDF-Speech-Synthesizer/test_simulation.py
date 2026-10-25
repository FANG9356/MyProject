import os
import sys
from pdf_to_speech import extract_text_from_pdf, convert_text_to_thai_speech

def run_tests():
    pdf_path = os.path.join(os.path.dirname(__file__), "locate.pdf")
    assert os.path.exists(pdf_path), "locate.pdf must exist"

    extracted = extract_text_from_pdf(pdf_path)
    assert len(extracted) > 0, "Extracted text should not be empty"

    out_file = os.path.join(os.path.dirname(__file__), "test_speech.mp3")
    if os.path.exists(out_file):
        os.remove(out_file)

    sample_sentence = "สวัสดีครับ นี่คือระบบแปลงข้อความเป็นเสียงภาษาไทย"
    convert_text_to_thai_speech(sample_sentence, out_file)
    assert os.path.exists(out_file), "Output mp3 must be created"
    assert os.path.getsize(out_file) > 1000, "MP3 file must have valid audio size"

    print("Project 22 PDF Speech Synthesizer tests passed")

if __name__ == "__main__":
    run_tests()
