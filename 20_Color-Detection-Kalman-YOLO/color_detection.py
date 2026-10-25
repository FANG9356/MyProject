import cv2
import numpy as np


def get_dominant_color(image_bgr: np.ndarray, k: int = 3) -> tuple:
    """
    รับภาพ BGR (จากการ crop ตาม bounding box ของ YOLO)
    คืนค่าสีเด่นที่สุดในรูปแบบ (B, G, R)
    """
    small = cv2.resize(image_bgr, (50, 50), interpolation=cv2.INTER_AREA)
    pixels = small.reshape(-1, 3).astype(np.float32)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(
        pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
    )

    counts = np.bincount(labels.flatten())
    dominant = centers[np.argmax(counts)]
    return tuple(int(c) for c in dominant)


def bgr_to_color_name(bgr: tuple) -> str:
    """
    แปลงค่าสี BGR เป็นชื่อสีพื้นฐาน โดยอิงจากช่วงค่า HSV
    (HSV ทนทานต่อการเปลี่ยนแปลงของแสงมากกว่า RGB)
    """
    b, g, r = bgr
    pixel = np.uint8([[[b, g, r]]])
    hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)[0][0]
    h, s, v = int(hsv[0]), int(hsv[1]), int(hsv[2])

    if v < 40:
        return "ดำ"
    if s < 40:
        return "ขาว" if v > 200 else "เทา"

    color_ranges = [
        (0, 10, "แดง"), (10, 25, "ส้ม"), (25, 35, "เหลือง"),
        (35, 85, "เขียว"), (85, 100, "ฟ้า"), (100, 130, "น้ำเงิน"),
        (130, 160, "ม่วง"), (160, 179, "แดง"),
    ]
    for lower, upper, name in color_ranges:
        if lower <= h < upper:
            return name
    return "ไม่ทราบ"


def detect_object_color(image_path: str, bbox: tuple) -> str:
    """
    bbox = (x1, y1, x2, y2) ที่ได้จากผลลัพธ์ YOLO
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"ไม่พบไฟล์รูปภาพ: {image_path}")
    x1, y1, x2, y2 = bbox
    cropped = image[y1:y2, x1:x2]

    dominant_bgr = get_dominant_color(cropped, k=3)
    color_name = bgr_to_color_name(dominant_bgr)
    return color_name


if __name__ == "__main__":
    image_path = "example.jpg"
    bbox = (100, 150, 300, 400)

    try:
        color = detect_object_color(image_path, bbox)
        print(f"สีของวัตถุที่ตรวจพบ: {color}")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
