import faster_whisper
import traceback

print("Testing large-v2...")
try:
    model = faster_whisper.WhisperModel("large-v2", device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        "Velika - ไม่ว่ากี่ปีแสง (Audio).mp3",
        beam_size=1,                  
        condition_on_previous_text=False,
        initial_prompt="เนื้อเพลงภาษาไทย",
    )
    for i, segment in enumerate(segments):
        if i > 10 and i < 20:                     
            print(f"[{segment.start:.2f}] {segment.text}")
        if i >= 20:
            break
except Exception as e:
    traceback.print_exc()
