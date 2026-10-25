import os
import shutil
import tempfile
import hashlib
from collections import defaultdict

def test_file_structure():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = [
        "clean.py",
        "docs/duplicate_detection_algorithm.md"
    ]
    for rel_path in files:
        full_path = os.path.join(base_dir, rel_path)
        assert os.path.exists(full_path), f"Missing file: {rel_path}"

def hash_file(file_path, block_size=65536):
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            buf = f.read(block_size)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(block_size)
        return hasher.hexdigest()
    except (IOError, PermissionError):
        return None

def find_duplicates(folder_path):
    files_by_size = defaultdict(list)
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if not os.path.exists(file_path) or not os.path.getsize(file_path) > 0:
                continue
            files_by_size[os.path.getsize(file_path)].append(file_path)

    duplicates = defaultdict(list)
    for size, files in files_by_size.items():
        if len(files) > 1:
            for file_path in files:
                file_hash = hash_file(file_path)
                if file_hash:
                    duplicates[file_hash].append(file_path)
    
    return {k: v for k, v in duplicates.items() if len(v) > 1}

def test_duplicate_detection_and_safe_delete():
    temp_dir = tempfile.mkdtemp(prefix="clean_test_")
    try:
        f_a1 = os.path.join(temp_dir, "report_v1.txt")
        f_a2 = os.path.join(temp_dir, "report_copy.txt")
        f_b = os.path.join(temp_dir, "unique_doc.txt")
        f_c1 = os.path.join(temp_dir, "image1.bin")
        f_c2 = os.path.join(temp_dir, "image_backup.bin")

        with open(f_a1, "w", encoding="utf-8") as f:
            f.write("Duplicate content payload alpha")
        with open(f_a2, "w", encoding="utf-8") as f:
            f.write("Duplicate content payload alpha")
        with open(f_b, "w", encoding="utf-8") as f:
            f.write("Completely unique content beta gamma")
        with open(f_c1, "wb") as f:
            f.write(b"\x00\xFF\xAA\x55" * 256)
        with open(f_c2, "wb") as f:
            f.write(b"\x00\xFF\xAA\x55" * 256)

        duplicates = find_duplicates(temp_dir)
        assert len(duplicates) == 2, f"Expected 2 duplicate groups, got {len(duplicates)}"

        all_dup_files = [p for paths in duplicates.values() for p in paths]
        assert f_a1 in all_dup_files and f_a2 in all_dup_files
        assert f_c1 in all_dup_files and f_c2 in all_dup_files
        assert f_b not in all_dup_files

        os.remove(f_a2)
        assert not os.path.exists(f_a2)
        assert os.path.exists(f_a1)

        post_cleanup = find_duplicates(temp_dir)
        assert len(post_cleanup) == 1
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    test_file_structure()
    test_duplicate_detection_and_safe_delete()
    print("Project 16: Duplicate File Cleaner simulation tests PASSED")
