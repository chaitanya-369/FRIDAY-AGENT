import os
import logging

try:
    from elevenlabs.client import ElevenLabs

    HAVE_ELEVENLABS = True
except ImportError:
    HAVE_ELEVENLABS = False

logger = logging.getLogger(__name__)


class TTSRouter:
    """
    Dynamic TTS Router:
    Uses ElevenLabs by default, but seamlessly falls back to Local TTS (e.g. Piper/Kokoro)
    if API credits are depleted or latency is too high.
    """

    def __init__(self):
        self.api_key = os.environ.get("ELEVENLABS_API_KEY") or os.environ.get(
            "ELEVEN_API_KEY"
        )
        self.voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "XrExE9yKIg1WjnnlVkGX")

        self.elevenlabs = None
        if HAVE_ELEVENLABS and self.api_key:
            self.elevenlabs = ElevenLabs(api_key=self.api_key)

        self.use_local = True if not self.elevenlabs else False

        # Piper config
        self.piper_model_path = os.environ.get("PIPER_MODEL_PATH")
        self.piper_config_path = os.environ.get("PIPER_CONFIG_PATH")
        self.piper_voice = None

        # Try to load local TTS
        self._init_local_tts()

    def _init_local_tts(self):
        try:
            import piper

            if self.piper_model_path and os.path.exists(self.piper_model_path):
                self.piper_voice = piper.PiperVoice.load(
                    self.piper_model_path, config_path=self.piper_config_path
                )
                logger.info(f"Local Piper TTS loaded: {self.piper_model_path}")
                return True
            else:
                logger.warning("Piper model file not found. Local TTS will be mock.")
                return False
        except ImportError:
            logger.warning("piper-tts not installed. Local TTS will be mocked.")
            return False

    def synthesize_stream(self, text_chunk):
        """
        Takes a string of text and yields PCM audio chunks (16000Hz, mono).
        """
        if not text_chunk.strip():
            return

        # If ElevenLabs is not configured, always use local
        if not self.elevenlabs:
            yield from self._synthesize_local(text_chunk)
            return

        if self.use_local:
            yield from self._synthesize_local(text_chunk)
        else:
            yielded_any = False
            try:
                for chunk in self._synthesize_elevenlabs(text_chunk):
                    if chunk:
                        yielded_any = True
                        yield chunk
            except Exception as e:
                logger.error(f"ElevenLabs TTS failed: {e}.")
                if not yielded_any:
                    logger.info("Falling back to Local TTS for this chunk.")
                    # Don't set self.use_local = True permanently
                    yield from self._synthesize_local(text_chunk)
                else:
                    logger.warning(
                        "ElevenLabs stream failed mid-sentence. Skipping fallback to avoid stutter."
                    )

    def _synthesize_elevenlabs(self, text):
        logger.debug(f"[ElevenLabs] Synthesizing: {text}")
        try:
            # ElevenLabs SDK 2.x usage
            audio_stream = self.elevenlabs.text_to_speech.stream(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2",  # Higher quality, widely available
                output_format="pcm_16000",
            )

            # The stream method returns an iterator of bytes
            for chunk in audio_stream:
                if chunk:
                    yield chunk

        except Exception as e:
            logger.error(f"ElevenLabs synthesis internal error: {e}")
            # Try secondary fallback with convert_as_stream if it exists
            # (sometimes it's preferred for specific output formats)
            try:
                logger.info("Attempting secondary fallback to convert_as_stream...")
                # Note: Some versions might still use convert_as_stream
                if hasattr(self.elevenlabs.text_to_speech, "convert_as_stream"):
                    audio_stream = self.elevenlabs.text_to_speech.convert_as_stream(
                        text=text,
                        voice_id=self.voice_id,
                        model_id="eleven_monolingual_v1",
                    )
                    for chunk in audio_stream:
                        yield chunk
                else:
                    raise e
            except Exception as e2:
                logger.error(f"ElevenLabs secondary fallback failed: {e2}")
                raise e2

    def _synthesize_local(self, text):
        logger.debug(f"[Local TTS] Synthesizing: {text}")
        if self.piper_voice:
            try:
                # Piper synthesize_stream yields raw PCM bytes
                for audio_bytes in self.piper_voice.synthesize_stream(text):
                    yield audio_bytes
            except Exception as e:
                logger.error(f"Local Piper synthesis error: {e}")
                yield b"\x00" * 3200  # Fallback silence
        else:
            # Yield silence (mock) to ensure the pipeline doesn't crash
            # while the actual local binary/model is missing.
            yield b"\x00" * 16000
