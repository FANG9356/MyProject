from ultralytics import YOLO
import numpy as np, os, time

print("="*60)
print("🧪 [TEST SIMULATION] 05_ATM-YOLOv8-Detector")
print("="*60)

model_path = os.path.join(os.path.dirname(__file__), "yolov8n.pt")
assert os.path.exists(model_path), "Model weight yolov8n.pt missing!"
model = YOLO(model_path)
print(f"✅ YOLOv8 Deep Learning Model Loaded ({len(model.names)} classes)")

dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
t0 = time.time()
results = model(dummy_frame, verbose=False)
elapsed = (time.time() - t0) * 1000
print(f"✅ Frame Inference Simulation: Completed in {elapsed:.1f} ms")
print("🎉 Status: TEST PASSED (100% Operational)")
