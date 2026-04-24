try:
    import pyaudio

    HAVE_PYAUDIO = True
except ImportError:
    HAVE_PYAUDIO = False
import queue
import logging

try:
    from webrtc_audio_processing import AudioProcessingModule

    HAVE_AEC = True
except ImportError:
    HAVE_AEC = False

logger = logging.getLogger(__name__)


class AudioIO:
    """
    Manages PyAudio streams for input (mic) and output (speaker).
    Provides queues for sending/receiving audio chunks.
    Implements software AEC (Acoustic Echo Cancellation) if available.
    """

    def __init__(self, sample_rate=16000, frame_duration_ms=30):
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.chunk_size = int(sample_rate * frame_duration_ms / 1000)

        self.p = None
        global HAVE_PYAUDIO
        if HAVE_PYAUDIO:
            try:
                self.p = pyaudio.PyAudio()
            except Exception as e:
                logger.error(f"Failed to initialize PyAudio: {e}")
                # We don't set HAVE_PYAUDIO to False here to avoid UnboundLocalError
                # but we check self.p throughout the class

        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

        self.input_stream = None
        self.output_stream = None

        self.running = False

        self.apm = None
        if HAVE_AEC:
            self.apm = AudioProcessingModule(aec=True, agc=True, ns=True)
            self.apm.set_stream_format(self.sample_rate, 1)

    def start(self):
        if not HAVE_PYAUDIO or not self.p:
            logger.warning("AudioIO: Cannot start, PyAudio not available.")
            return

        self.running = True

        try:
            self.input_stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._input_callback,
            )

            self.output_stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._output_callback,
            )

            self.input_stream.start_stream()
            self.output_stream.start_stream()
            logger.info(f"AudioIO started. AEC enabled: {HAVE_AEC}")
        except Exception as e:
            logger.error(f"Failed to open audio streams: {e}")
            self.running = False

    def stop(self):
        self.running = False
        if self.input_stream:
            try:
                self.input_stream.stop_stream()
                self.input_stream.close()
            except Exception:
                pass
        if self.output_stream:
            try:
                self.output_stream.stop_stream()
                self.output_stream.close()
            except Exception:
                pass
        if self.p:
            try:
                self.p.terminate()
            except Exception:
                pass
        logger.info("AudioIO stopped.")

    def _input_callback(self, in_data, frame_count, time_info, status):
        if self.running:
            # If we have AEC, process the near-end (mic) audio
            if self.apm:
                out_data = self.apm.process_stream(in_data)
                self.input_queue.put(out_data)
            else:
                self.input_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def _output_callback(self, in_data, frame_count, time_info, status):
        if not self.running:
            return (b"\x00" * (frame_count * 2), pyaudio.paComplete)

        try:
            # Non-blocking get
            out_data = self.output_queue.get_nowait()

            # If AEC is enabled, feed speaker audio to the APM reverse stream
            if self.apm:
                self.apm.analyze_reverse_stream(out_data)

            return (out_data, pyaudio.paContinue)
        except queue.Empty:
            # Play silence if queue is empty
            silence = b"\x00" * (frame_count * 2)
            if self.apm:
                self.apm.analyze_reverse_stream(silence)
            return (silence, pyaudio.paContinue)

    def play_audio(self, pcm_data):
        """Enqueue PCM data to be played on the speaker."""
        bytes_per_sample = 2
        bytes_per_chunk = self.chunk_size * bytes_per_sample
        for i in range(0, len(pcm_data), bytes_per_chunk):
            chunk = pcm_data[i : i + bytes_per_chunk]
            if len(chunk) < bytes_per_chunk:
                chunk += b"\x00" * (bytes_per_chunk - len(chunk))
            self.output_queue.put(chunk)

    def flush_output(self):
        """Immediately clear the output queue (e.g., on interrupt)."""
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except queue.Empty:
                break

    def flush_input(self):
        """Immediately clear the input queue to drop stale audio frames."""
        while not self.input_queue.empty():
            try:
                self.input_queue.get_nowait()
            except queue.Empty:
                break

    def get_input_frame(self, block=True, timeout=None):
        return self.input_queue.get(block=block, timeout=timeout)
