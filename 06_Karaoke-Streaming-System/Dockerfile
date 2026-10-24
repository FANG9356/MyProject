# ใช้ Python 3.11 ตัว slim เพื่อให้ Image มีขนาดเล็ก
FROM python:3.11-slim

# อัปเดตแพ็กเกจ และติดตั้ง ffmpeg ที่ yt-dlp ต้องใช้ในการมัดรวมไฟล์
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ตั้งค่า Directory หลักที่จะทำงานใน Container
WORKDIR /app

# ก๊อปปี้ไฟล์ requirements.txt มาก่อนเพื่อติดตั้ง Library
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ก๊อปปี้ไฟล์โปรเจกต์ทั้งหมดของฟางเข้ามา
COPY . .

# เปิดพอร์ต 8000 ให้คนข้างนอกเข้ามาคุยด้วยได้
EXPOSE 8000

# คำสั่งรันเซิร์ฟเวอร์ด้วย uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]