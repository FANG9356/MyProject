import os
import json
import re

def test_file_structure():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = [
        "index.html",
        "css/c.css",
        "script/s.js",
        "json/q.json",
        "picture/bow.png",
        "docs/quiz_question_bank_summary.md"
    ]
    for rel_path in files:
        full_path = os.path.join(base_dir, rel_path)
        assert os.path.exists(full_path), f"Missing file: {rel_path}"

def test_question_bank_integrity():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, "json/q.json")
    with open(json_path, "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    assert len(questions) == 400, f"Expected 400 questions, got {len(questions)}"
    for idx, q in enumerate(questions):
        assert "question" in q, f"Question {idx} missing 'question'"
        assert "options" in q, f"Question {idx} missing 'options'"
        assert "correctAnswer" in q, f"Question {idx} missing 'correctAnswer'"
        assert len(q["options"]) == 4, f"Question {idx} does not have 4 options"
        assert q["correctAnswer"] in q["options"], f"Question {idx} correctAnswer not in options"

def test_student_validation():
    id_pattern = re.compile(r"^\d+$")
    assert bool(id_pattern.match("12345")) is True
    assert bool(id_pattern.match("abc")) is False
    assert bool(id_pattern.match("12a45")) is False

def test_quiz_scoring_simulation():
    total = 400
    correct = 350
    wrong = total - correct
    percentage = (correct / total) * 100
    scaled = correct / 3
    assert wrong == 50
    assert abs(percentage - 87.5) < 0.01
    assert abs(scaled - 116.666) < 0.01

if __name__ == "__main__":
    test_file_structure()
    test_question_bank_integrity()
    test_student_validation()
    test_quiz_scoring_simulation()
    print("Project 14: Computer Quiz System simulation tests PASSED")
