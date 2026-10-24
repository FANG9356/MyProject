import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

print("="*50)
print("🧠 Phase 2: AI Training (Machine Learning)")
print("="*50)

# 1. โหลดข้อมูลคลื่นวิทยุทั้ง 3 ท่าทาง
print("📂 กำลังโหลดข้อมูลคลื่นวิทยุ...")
files = ['dataset_empty.csv', 'dataset_walking.csv', 'dataset_falling.csv']

dataframes = []
for file in files:
    if os.path.exists(file):
        df = pd.read_csv(file)
        dataframes.append(df)
        print(f"  - โหลดไฟล์ {file} สำเร็จ ({len(df)} ตัวอย่าง)")
    else:
        print(f"  ❌ ไม่พบไฟล์ {file}")

if not dataframes:
    print("ไม่พบข้อมูลเลย โปรดกลับไปทำ Phase 1 ใหม่ครับ")
    exit()

# รวมข้อมูลทั้งหมดเป็นก้อนเดียว
dataset = pd.concat(dataframes, ignore_index=True)

# 2. แยก Features (คลื่น 64 เส้น) และ Labels (ชื่อท่าทาง)
X = dataset.drop('Label', axis=1) # ข้อมูลคลื่นเพียวๆ
y = dataset['Label'] # คำเฉลย (Empty, Walking, Falling)

# 3. แบ่งข้อมูลเป็น 2 ส่วน: ส่วนที่ใช้สอน (80%) และส่วนที่ใช้สอบข้อเขียน (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("\n🤖 กำลังส่งข้อมูลเข้าสู่สมองกล AI (Random Forest)...")
# 4. สร้างสมองกล AI (Random Forest คือการสร้างต้นไม้ตัดสินใจหลายๆ ต้นมาช่วยกันโหวต)
ai_model = RandomForestClassifier(n_estimators=100, random_state=42)

# 5. สั่งให้ AI เรียนรู้แพทเทิร์นของคลื่น (Training)
ai_model.fit(X_train, y_train)

# 6. ทดสอบความฉลาดของ AI
y_pred = ai_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("="*50)
print(f"🏆 AI เรียนรู้เสร็จสิ้น! ความแม่นยำในการทายผล: {accuracy * 100:.2f}%")
print("="*50)
print("\nรายละเอียดความแม่นยำแยกตามท่าทาง:")
print(classification_report(y_test, y_pred))

# 7. เซฟสมองกลที่เรียนรู้เสร็จแล้วเป็นไฟล์เก็บไว้ใช้งานใน Phase 3
model_filename = 'ai_model.pkl'
joblib.dump(ai_model, model_filename)
print(f"💾 เซฟสมองกลลงไฟล์ '{model_filename}' เรียบร้อยแล้ว! พร้อมลุย Phase 3!")
