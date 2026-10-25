import os

def test_file_structure():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = [
        "cal.py",
        "docs/grading_system_manual.md"
    ]
    for rel_path in files:
        full_path = os.path.join(base_dir, rel_path)
        assert os.path.exists(full_path), f"Missing file: {rel_path}"

def get_grade_point(score):
    if score >= 80: return 4.0
    elif score >= 75: return 3.5
    elif score >= 70: return 3.0
    elif score >= 65: return 2.5
    elif score >= 60: return 2.0
    elif score >= 55: return 1.5
    elif score >= 50: return 1.0
    else: return 0.0

def get_grade(score):
    if score >= 80: return "A"
    elif score >= 75: return "B+"
    elif score >= 70: return "B"
    elif score >= 65: return "C+"
    elif score >= 60: return "C"
    elif score >= 55: return "D+"
    elif score >= 50: return "D"
    else: return "F"

def test_grade_mapping():
    assert get_grade(85) == "A" and get_grade_point(85) == 4.0
    assert get_grade(76) == "B+" and get_grade_point(76) == 3.5
    assert get_grade(72) == "B" and get_grade_point(72) == 3.0
    assert get_grade(67) == "C+" and get_grade_point(67) == 2.5
    assert get_grade(62) == "C" and get_grade_point(62) == 2.0
    assert get_grade(58) == "D+" and get_grade_point(58) == 1.5
    assert get_grade(51) == "D" and get_grade_point(51) == 1.0
    assert get_grade(45) == "F" and get_grade_point(45) == 0.0

def test_gpa_calculation():
    records = [
        {"credit": 3.0, "grade_point": 4.0},
        {"credit": 3.0, "grade_point": 3.0},
        {"credit": 2.0, "grade_point": 3.5}
    ]
    total_credit = sum(r["credit"] for r in records)
    total_points = sum(r["credit"] * r["grade_point"] for r in records)
    gpa = total_points / total_credit
    assert total_credit == 8.0
    assert total_points == 28.0
    assert abs(gpa - 3.50) < 0.001

def test_gpax_calculation():
    prev_gpa = 3.20
    prev_credit = 30.0
    current_credits = 8.0
    current_points = 28.0

    numerator = (prev_gpa * prev_credit) + current_points
    denominator = prev_credit + current_credits
    gpax = numerator / denominator
    assert denominator == 38.0
    assert abs(gpax - 3.263) < 0.01

if __name__ == "__main__":
    test_file_structure()
    test_grade_mapping()
    test_gpa_calculation()
    test_gpax_calculation()
    print("Project 17: Grade Calculator simulation tests PASSED")
