import threading
import logging
import time
import queue

from .audio_io import AudioIO
from .vad_engine import VADEngine
from .stt_whisper import LocalSTT
from .tts_streamer import TTSRouter

logger = logging.getLogger(__name__)


class VoicePipeline:
    """
    The orchestrator for the FRIDAY Voice Pipeline.
    Manages State Machine: STANDBY -> LISTENING -> PROCESSING -> SPEAKING -> (INTERRUPT)
    """

    def __init__(self, brain_instance):
        self.brain = brain_instance
        self.audio = AudioIO()
        self.vad = VADEngine()
        self.stt = LocalSTT()
        self.tts = TTSRouter()

        self.state = "STANDBY"
        self.running = False
        self.interrupt_event = threading.Event()
        self.audio_buffer_to_process = []
        self.last_wake_time = 0
        self.speaking_start_time = 0

    def start(self):
        self.running = True
        self.audio.start()

        # Start main loop in background
        self.main_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.main_thread.start()

        logger.info("Voice Pipeline started. Waiting for wake word or input.")

    def stop(self):
        self.running = False
        self.audio.stop()
        if hasattr(self, "main_thread"):
            self.main_thread.join(timeout=2)

    def _run_loop(self):
        while self.running:
            if self.state == "STANDBY":
                self._standby_loop()
            elif self.state == "LISTENING":
                self._listening_loop()
            elif self.state == "PROCESSING":
                self._processing_loop()
            elif self.state == "SPEAKING":
                self._speaking_loop()

    def _standby_loop(self):
        try:
            frame = self.audio.get_input_frame(timeout=0.1)
            # Only allow wake word if we haven't just finished speaking (2s cooldown)
            if time.time() - self.last_wake_time > 2.0:
                if self.vad.is_wake_word(frame):
                    logger.info("[State] WAKE WORD DETECTED -> LISTENING")
                    self.last_wake_time = time.time()
                    self.state = "LISTENING"
        except queue.Empty:
            pass

    def _listening_loop(self):
        audio_buffer = []
        silence_frames = 0
        max_silence = 30  # ~900ms (Increased from 15 to allow more natural pauses)
        max_listen_time = 15.0  # Stop after 15 seconds (Increased from 8s)
        start_time = time.time()

        logger.info("FRIDAY is recording your command...")

        while self.running and self.state == "LISTENING":
            try:
                if time.time() - start_time > max_listen_time:
                    logger.warning("[State] LISTEN TIMEOUT -> PROCESSING")
                    self.audio_buffer_to_process = audio_buffer
                    self.state = "PROCESSING"
                    break

                frame = self.audio.get_input_frame(timeout=0.1)
                audio_buffer.append(frame)

                is_speech = self.vad.is_speech(frame)
                if is_speech:
                    silence_frames = 0
                else:
                    silence_frames += 1

                # Periodically log VAD status
                if len(audio_buffer) % 20 == 0:
                    logger.debug(
                        f"Listening: {len(audio_buffer)} frames, silence_frames: {silence_frames}"
                    )

                if (
                    silence_frames > max_silence
                    and len(audio_buffer) > max_silence + 10
                ):
                    logger.info(
                        f"[State] SILENCE DETECTED ({silence_frames} frames) -> PROCESSING"
                    )
                    self.audio_buffer_to_process = audio_buffer
                    self.state = "PROCESSING"
                    break
            except queue.Empty:
                continue

    def _processing_loop(self):
        logger.info("Transcribing audio...")
        text = self.stt.transcribe(self.audio_buffer_to_process)
        self.audio_buffer_to_process = []

        # Filter out Whisper hallucinations (common short words on noise)
        if not text or text.lower().strip() in [
            "you",
            "you.",
            "yes.",
            "yes",
            "the",
            "a",
        ]:
            logger.info(f"Filtered potential hallucination: '{text}'. Back to STANDBY.")
            self.audio.flush_input()
            self.state = "STANDBY"
            return

        logger.info(f"User said: {text}")

        # Reset interrupt
        self.interrupt_event.clear()
        self.speaking_start_time = time.time()
        self.audio.flush_input()
        self.state = "SPEAKING"

        # Start Brain process in a separate thread to allow stream playback
        threading.Thread(
            target=self._process_brain_and_speak, args=(text,), daemon=True
        ).start()

    def _process_brain_and_speak(self, text):
        logger.info("Passing to Brain...")
        try:
            # Stream tokens from brain
            token_stream = self.brain.stream_process(text)

            spoken_sentences = []
            current_sentence = ""

            for token in token_stream:
                if self.interrupt_event.is_set():
                    logger.warning("Generation interrupted!")
                    break

                current_sentence += token

                # Simple sentence boundary detection
                if any(punct in token for punct in [". ", "? ", "! ", ".\n"]):
                    sentence_to_speak = current_sentence.strip()
                    current_sentence = ""

                    if sentence_to_speak:
                        audio_chunks = self.tts.synthesize_stream(sentence_to_speak)
                        for chunk in audio_chunks:
                            if self.interrupt_event.is_set():
                                break
                            self.audio.play_audio(chunk)

                        if not self.interrupt_event.is_set():
                            spoken_sentences.append(sentence_to_speak)

            # Handle remainder
            if current_sentence.strip() and not self.interrupt_event.is_set():
                audio_chunks = self.tts.synthesize_stream(current_sentence.strip())
                for chunk in audio_chunks:
                    if self.interrupt_event.is_set():
                        break
                    self.audio.play_audio(chunk)
                if not self.interrupt_event.is_set():
                    spoken_sentences.append(current_sentence.strip())

            # Commit only what was spoken
            if hasattr(self.brain, "commit_memory_explicit"):
                self.brain.commit_memory_explicit(text, " ".join(spoken_sentences))

        except Exception as e:
            logger.error(f"Error in Brain processing: {e}")

        if self.state == "SPEAKING" and not self.interrupt_event.is_set():
            logger.info("[State] Finished SPEAKING -> STANDBY")
            self.audio.flush_input()
            self.state = "STANDBY"

    def _speaking_loop(self):
        # While speaking, we monitor for interrupt
        try:
            frame = self.audio.get_input_frame(timeout=0.1)

            # 1. Check for wake word (Jarvis) during speech
            # Always pass the frame to keep OpenWakeWord's internal buffer updated
            is_interrupt = self.vad.is_wake_word_interrupt(frame)

            # Higher threshold and longer delay to prevent self-interruption
            if time.time() - self.speaking_start_time > 5.0:
                if is_interrupt:
                    logger.warning("[State] WAKE WORD INTERRUPT -> STANDBY")
                    self.last_wake_time = time.time()  # Cooldown
                    self.interrupt_event.set()
                    self.audio.flush_output()
                    self.audio.flush_input()
                    self.state = "STANDBY"
                    return

            # 2. Manual trigger from keyboard can always interrupt
            if self.interrupt_event.is_set():
                self.audio.flush_input()
                self.state = "STANDBY"

        except queue.Empty:
            pass
