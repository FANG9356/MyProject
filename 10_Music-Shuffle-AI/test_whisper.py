import faster_whisper
import traceback
import sys

print("Loading model...")
model_dir = "ai_models"
model = faster_whisper.WhisperModel("large-v3", device="cpu", compute_type="int8", download_root=model_dir)

print("Transcribing...")
try:
    segments, info = model.transcribe(
        "Velika - ไม่ว่ากี่ปีแสง (Audio).mp3", 
        beam_size=5,
        condition_on_previous_text=False,
        initial_prompt="เนื้อเพลง ร้องเพลง เพลงไทย เพลงสากล English song lyrics.",
        compression_ratio_threshold=2.4,
        logprob_threshold=-1.0
    )
    for segment in segments:
        print(segment.text)
except Exception as e:
    traceback.print_exc()
