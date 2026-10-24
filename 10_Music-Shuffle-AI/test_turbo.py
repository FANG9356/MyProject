import faster_whisper
import traceback

print("Loading turbo model...")
try:
    model = faster_whisper.WhisperModel("deepdml/faster-whisper-large-v3-turbo-ct2", device="cpu", compute_type="int8")
    print("Turbo model loaded successfully!")

    segments, info = model.transcribe(
        "Velika - ไม่ว่ากี่ปีแสง (Audio).mp3",
        beam_size=5,
        word_timestamps=True
    )
    for i, segment in enumerate(segments):
        if i < 5:
            print(f"[{segment.start:.2f}] {segment.text}")
        else:
            break
except Exception as e:
    traceback.print_exc()
