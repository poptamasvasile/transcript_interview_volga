import os
import assemblyai as aai
import os
from dotenv import load_dotenv
load_dotenv()
aai.settings.api_key = os.environ["ASSEMBLYAI_API_KEY"]


# ── Step 1: Audio file loader ────────────────────────────────────────────────

class AudioLoader:
    """Loads and validates an audio file. Supports multiple formats.
    https://www.assemblyai.com/docs/faq/what-audio-and-video-file-types-are-supported-by-your-api"""

    SUPPORTED_FORMATS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".mp4", ".webm"}

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._validate()

    def _validate(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Audio file not found: {self.file_path}")
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format '{ext}'. Supported formats: {self.SUPPORTED_FORMATS}"
            )

    def load(self) -> str:
        return self.file_path


# ── Step 2: Transcription ────────────────────────────────────────────────────

def transcribe(file_path: str) -> aai.Transcript:
    """Transcribes an audio file and returns the full AssemblyAI Transcript object."""
    config = aai.TranscriptionConfig(speech_models=["universal-2"])
    transcript = aai.Transcriber().transcribe(file_path, config=config)

    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(f"Transcription failed: {transcript.error}")

    return transcript


# ── Step 3: Service — transcription with timestamps per segment ──────────────

def get_segments(transcript: aai.Transcript) -> list[dict]:
    """Returns a list of sentence-level segments, each with start/end timestamps."""
    return [
        {
            "start_ms": sentence.start,
            "end_ms": sentence.end,
            "text": sentence.text,
        }
        for sentence in transcript.get_sentences()
    ]


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    audio_file = r"C:\Users\volteanu\Desktop\interviu\transcription-pipeline\harvard.wav"

    # Step 1 — load & validate
    loader = AudioLoader(audio_file)
    file_path = loader.load()

    # Step 2 — transcribe
    transcript = transcribe(file_path)
    print("Full transcription:")
    print(transcript.text)

    # Step 3 — segments with timestamps
    segments = get_segments(transcript)
    print("\nSegments with timestamps:")
    for seg in segments:
        start = seg["start_ms"] / 1000
        end = seg["end_ms"] / 1000
        print(f"[{start:.2f}s – {end:.2f}s]  {seg['text']}")
