# 🌟 Stage 1: สร้างเครื่องสำหรับ Build (ตั้งชื่อว่า builder)
FROM 192.168.1.1:8080/node:latest AS builder
WORKDIR /app
# ก๊อปปี้ไฟล์รายการแพ็กเกจมาติดตั้งก่อน (ช่วยให้ Docker ทำงานเร็วขึ้นในรอบหน้า)
COPY package*.json ./
RUN npm install --registry=http://192.168.1.1:4873
# ก๊อปปี้โค้ดทั้งหมดมา แล้วสั่ง Build! (ไม่ต้องพิมพ์เองแล้ว)
COPY . .
RUN npm run build

# 🌟 Stage 2: สร้างเครื่องสำหรับรันจริง (Production)
FROM 192.168.1.1:8080/node:latest
WORKDIR /app
# ตั้งค่า Timezone ให้เป็น UTC สอดคล้องกับระบบเดิม
ENV TZ=UTC
# 🌟 เพิ่ม 2 บรรทัดนี้: บังคับให้ Nuxt 3 เปิดรับการเชื่อมต่อจาก Nginx
ENV HOST=0.0.0.0
ENV PORT=80

# ก๊อปปี้เฉพาะโฟลเดอร์ .output ที่บิลด์เสร็จแล้วจาก Stage 1 มาใช้ (ทิ้งโค้ดขยะไว้ข้างหลัง)
COPY --from=builder /app/.output ./.output

EXPOSE 80
# สั่งรันเซิร์ฟเวอร์ของ Nuxt 3
CMD ["node", ".output/server/index.mjs"]