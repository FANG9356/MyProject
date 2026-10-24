import faster_whisper
import traceback

print("Testing strict thresholds...")
try:
    model = faster_whisper.WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        "Velika - ไม่ว่ากี่ปีแสง (Audio).mp3",
        beam_size=5,
        word_timestamps=True,
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=1000, speech_pad_ms=400),
        log_prob_threshold=-0.5,                      
        no_speech_threshold=0.4,                             
    )
    for i, segment in enumerate(segments):
        if i > 5 and i < 15:
            print(f"[{segment.start:.2f}] {segment.text} (logprob: {segment.avg_logprob:.2f}, no_speech: {segment.no_speech_prob:.2f})")
        if i >= 15:
            break
except Exception as e:
    traceback.print_exc()
