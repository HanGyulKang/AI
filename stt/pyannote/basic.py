# https://huggingface.co/pyannote/speaker-diarization-3.1

from pyaannote.audio import Pipeline

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")

diarization = pipeline("audio.wav")

for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"Speaker {speaker} from {turn.start} to {turn.end}")