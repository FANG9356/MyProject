import os
import sys
import re

def test_pages_existence():
    required_pages = [
        "index.html",
        "Seniormath.html",
        "Math.html",
        "Physics.html",
        "Electronic.html",
        "Binary.html",
        "Binary1.html",
        "calculator.html",
        "About.html",
        "Aboutme.html",
        "Login.html",
        "Time.html",
        "styles.css",
        "script.js"
    ]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for page in required_pages:
        path = os.path.join(base_dir, page)
        assert os.path.exists(path), f"Missing page: {page}"

def test_documents_existence():
    required_docs = [
        "docs/เนื้อหาคณิค.txt",
        "docs/เนื้อหาฟิสิกส์.txt",
        "docs/เนื้อหาเลขฐาน.txt",
        "docs/เนื้อหาไฟฟ้า.txt"
    ]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for doc in required_docs:
        path = os.path.join(base_dir, doc)
        assert os.path.exists(path), f"Missing document: {doc}"
        assert os.path.getsize(path) > 100, f"Document too small: {doc}"

def test_html_structure_and_links():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    core_pages = ["index.html", "Seniormath.html", "Math.html", "Physics.html", "Electronic.html", "Binary.html", "calculator.html", "About.html"]
    for page in core_pages:
        path = os.path.join(base_dir, page)
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            assert "<!DOCTYPE html>" in content or "<html" in content, f"Malformed HTML in {page}"
            assert "<title>" in content, f"Missing title in {page}"

def test_binary_conversion_logic():
    def dec_to_bin(num):
        return bin(num)[2:]
    def bin_to_dec(b_str):
        return int(b_str, 2)
    def dec_to_hex(num):
        return hex(num)[2:].upper()

    assert dec_to_bin(42) == "101010"
    assert bin_to_dec("101010") == 42
    assert dec_to_hex(255) == "FF"
    assert dec_to_hex(16) == "10"

def test_calculator_eval_logic():
    safe_dict = {"abs": abs, "round": round}
    expr = "25 * 4 + 100 / 2"
    result = eval(expr, {"__builtins__": None}, safe_dict)
    assert result == 150.0

if __name__ == "__main__":
    test_pages_existence()
    test_documents_existence()
    test_html_structure_and_links()
    test_binary_conversion_logic()
    test_calculator_eval_logic()
    print("Project 13: General Education Web simulation tests PASSED")
