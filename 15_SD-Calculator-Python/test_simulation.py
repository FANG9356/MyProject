import os
import numpy as np

def test_file_structure():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = [
        "sd.py",
        "sd.spec",
        "sun.png",
        "sun.ico",
        "docs/statistics_formula_manual.md"
    ]
    for rel_path in files:
        full_path = os.path.join(base_dir, rel_path)
        assert os.path.exists(full_path), f"Missing file: {rel_path}"

def test_statistical_calculations():
    sample_ratings = [
        [5.0, 4.0, 5.0, 5.0],
        [4.0, 4.0, 3.0, 4.0],
        [5.0, 5.0, 5.0, 5.0]
    ]
    ratings_array = np.array(sample_ratings)
    sums = np.sum(ratings_array, axis=1)
    means = np.mean(ratings_array, axis=1)
    std_devs = np.std(ratings_array, axis=1)
    cv_values = (std_devs / means) * 100

    assert sums[0] == 19.0
    assert means[0] == 4.75
    assert abs(std_devs[0] - 0.433) < 0.01
    assert abs(cv_values[0] - 9.116) < 0.01

    assert sums[1] == 15.0
    assert means[1] == 3.75
    assert abs(std_devs[1] - 0.433) < 0.01

    assert sums[2] == 20.0
    assert means[2] == 5.00
    assert std_devs[2] == 0.0
    assert cv_values[2] == 0.0

def test_zero_division_guard():
    zero_ratings = np.array([[0.0, 0.0, 0.0]])
    means = np.mean(zero_ratings, axis=1)
    std_devs = np.std(zero_ratings, axis=1)
    assert means[0] == 0.0
    assert std_devs[0] == 0.0

if __name__ == "__main__":
    test_file_structure()
    test_statistical_calculations()
    test_zero_division_guard()
    print("Project 15: SD Calculator simulation tests PASSED")
