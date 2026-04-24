import logging
import numpy as np

try:
    from openwakeword.model import Model
    import webrtcvad

    HAVE_VOICE_LIBS = True
except ImportError:
    HAVE_VOICE_LIBS = False

logger = logging.getLogger(__name__)


class VADEngine:
    """
    Handles Wake Word detection (OpenWakeWord) and Silence detection (WebRTC VAD).
    """

    def __init__(self, sample_rate=16000, vad_aggressiveness=3):
        self.sample_rate = sample_rate
        self.oww_model = None
        self.vad = None

        if HAVE_VOICE_LIBS:
            try:
                # Initialize OpenWakeWord with only the target wake word
                self.oww_model = Model(
                    wakeword_models=["hey_jarvis"], inference_framework="onnx"
                )
                logger.info("OpenWakeWord initialized with 'hey_jarvis' model.")
            except Exception as e:
                logger.warning(f"Failed to load OpenWakeWord: {e}")

            try:
                self.vad = webrtcvad.Vad(vad_aggressiveness)
            except Exception as e:
                logger.warning(f"Failed to load WebRTC VAD: {e}")

    def is_wake_word(self, pcm_data):
        if not self.oww_model:
            return False

        audio_int16 = np.frombuffer(pcm_data, dtype=np.int16)
        prediction = self.oww_model.predict(audio_int16)

        for name, val in prediction.items():
            if val > 0.4:  # Log even low confidence hits for debugging
                logger.debug(f"Wake word score [{name}]: {val:.2f}")
            if val > 0.6:  # Lowered from 0.8 for more sensitivity
                logger.info(f"CONFIRMED WAKE WORD [{name}]: {val:.2f}")
                return True
        return False

    def is_wake_word_interrupt(self, pcm_data):
        """Higher threshold for interrupts while already speaking."""
        if not self.oww_model:
            return False
        audio_int16 = np.frombuffer(pcm_data, dtype=np.int16)
        prediction = self.oww_model.predict(audio_int16)
        for name, val in prediction.items():
            if val > 0.8:  # Lowered from 0.95 to make it easier to stop
                logger.info(f"INTERRUPT WAKE WORD [{name}]: {val:.2f}")
                return True
        return False

    def is_speech(self, pcm_data):
        """
        VAD check to see if someone is talking (used to detect end of sentence).
        """
        if not self.vad:
            return False

        # WebRTC VAD requires frames of 10, 20, or 30ms
        # 480 samples = 30ms at 16kHz (960 bytes)
        if len(pcm_data) >= 960:
            pcm_data = pcm_data[:960]
        elif len(pcm_data) >= 640:
            pcm_data = pcm_data[:640]
        elif len(pcm_data) >= 320:
            pcm_data = pcm_data[:320]
        else:
            pcm_data = pcm_data.ljust(320, b"\x00")

        try:
            return self.vad.is_speech(pcm_data, self.sample_rate)
        except Exception:
            return False
