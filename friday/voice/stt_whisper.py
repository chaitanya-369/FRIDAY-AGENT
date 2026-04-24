import logging
import numpy as np

try:
    from faster_whisper import WhisperModel

    HAVE_WHISPER = True
except ImportError:
    HAVE_WHISPER = False

logger = logging.getLogger(__name__)


class LocalSTT:
    """
    Runs Faster-Whisper locally for secure, low-latency Speech-To-Text.
    """

    def __init__(self, model_size="base.en", device="cpu", compute_type="int8"):
        self.model = None
        if HAVE_WHISPER:
            logger.info(f"Loading Local STT ({model_size}) on {device}...")
            try:
                self.model = WhisperModel(
                    model_size, device=device, compute_type=compute_type
                )
            except Exception as e:
                logger.error(f"Failed to load WhisperModel: {e}")
        else:
            logger.warning("faster-whisper is not installed. STT is disabled.")

    def transcribe(self, pcm_frames):
        """Transcribe a list of raw PCM audio frames."""
        if not self.model or not pcm_frames:
            return ""

        audio_bytes = b"".join(pcm_frames)

        # Convert 16-bit PCM to float32 expected by whisper
        audio_np = (
            np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        )

        try:
            segments, _ = self.model.transcribe(audio_np, beam_size=5)
            text = " ".join([segment.text for segment in segments]).strip()
            return text
        except Exception as e:
            logger.error(f"STT Transcription failed: {e}")
            return ""
