import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional

from classanalizer.config import WHISPER_MODEL


class Transcriber:
    """Transcribe audio localmente con faster-whisper."""

    def __init__(self, model_size: Optional[str] = None):
        self.model_size = model_size or WHISPER_MODEL or "large-v3"
        self._model = None

    def _get_model(self):
        """Carga el modelo bajo demanda para no consumir memoria al iniciar la app."""
        if self._model is None:
            from faster_whisper import WhisperModel

            self._model = WhisperModel(
                self.model_size,
                device="auto",
                compute_type="auto",
            )
        return self._model

    @staticmethod
    def _extract_audio_for_stt(file_path: Path) -> tuple[Path, bool]:
        """Convierte audio/video a WAV mono de 16 kHz para Whisper."""
        video_extensions = {".mp4", ".mkv", ".mov", ".avi", ".webm"}
        needs_conversion = (
            file_path.suffix.lower() in video_extensions
            or file_path.suffix.lower() != ".wav"
        )

        if needs_conversion:
            temp_audio = Path(tempfile.gettempdir()) / (
                f"stt_{file_path.stem}_{int(time.time())}.wav"
            )
            cmd = [
                "ffmpeg", "-y", "-i", str(file_path),
                "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
                str(temp_audio),
            ]
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return temp_audio, True

        return file_path, False

    def transcribe(self, audio_path: Path, language: str = "es") -> str:
        """Devuelve la transcripción completa de un archivo de audio/video."""
        if not audio_path.exists():
            raise FileNotFoundError(f"El archivo no existe: {audio_path}")

        proc_path, is_temp = self._extract_audio_for_stt(audio_path)
        try:
            model = self._get_model()
            segments, _ = model.transcribe(
                str(proc_path),
                language=language,
                beam_size=5,
                word_timestamps=False,
                vad_filter=True,
            )
            return " ".join(segment.text.strip() for segment in segments).strip()
        finally:
            if is_temp and proc_path.exists():
                proc_path.unlink(missing_ok=True)
