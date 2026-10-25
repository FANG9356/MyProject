# ใช้ Node.js เวอร์ชั่นเบาบาง (alpine)
FROM 192.168.1.1:8080/node:latest
WORKDIR /app

# ตั้งค่า Timezone เป็น UTC 
ENV TZ=UTC

# 🌟 เพิ่ม 2 บรรทัดนี้: บังคับพอร์ต 8000 และเปิดรับ Nginx
ENV PORT=8000
ENV HOST=0.0.0.0

# ติดตั้งเฉพาะแพ็กเกจที่จำเป็นสำหรับใช้งานจริง (--omit=dev ตัดพวก nodemon ทิ้งไปเลย)
COPY package*.json ./
RUN npm install --omit=dev --registry=http://192.168.1.1:4873

# ก๊อปปี้โค้ด Backend ทั้งหมดลงไป
COPY . .

EXPOSE 8000
# สั่งรันไฟล์หลักของ Backend (เปลี่ยน server.js เป็นชื่อไฟล์หลักที่คุณครูใช้ครับ เช่น app.js หรือ index.js)
CMD ["node", "server.js"]