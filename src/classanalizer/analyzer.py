import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Tuple, Optional
from google import genai
from google.genai import types

from classanalizer.config import GEMINI_API_KEY, GEMINI_MODEL
from classanalizer.prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT_TEMPLATE


class GeminiAnalyzer:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError(
                "No se encontró GEMINI_API_KEY. Configúrala en el archivo .env o en tus variables de entorno.\n"
                "Puedes obtener tu clave gratuita en: https://aistudio.google.com/app/apikey"
            )
        self.model = model or GEMINI_MODEL
        self.client = genai.Client(api_key=self.api_key)

    @staticmethod
    def _extract_audio_if_video(file_path: Path) -> Tuple[Path, bool]:
        """Si el archivo es un video (.mp4, .mkv, .mov, etc.), extrae solo el audio MP3 para reducir tamaño un 90%."""
        video_extensions = {".mp4", ".mkv", ".mov", ".avi", ".webm"}
        if file_path.suffix.lower() in video_extensions:
            temp_audio = Path(tempfile.gettempdir()) / f"extracted_{file_path.stem}_{int(time.time())}.mp3"
            cmd = [
                "ffmpeg", "-y", "-i", str(file_path),
                "-vn", "-c:a", "libmp3lame", "-b:a", "96k", "-ar", "44100",
                str(temp_audio)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return temp_audio, True
        return file_path, False

    def _call_gemini_with_resilience(self, audio_file_upload, prompt: str):
        # Lista ordenada de modelos a probar
        candidate_models = [self.model, "gemini-3.6-flash", "gemini-flash-latest", "gemini-2.5-pro"]
        seen = set()
        models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

        last_error = None
        for model_name in models_to_try:
            # Reintentar hasta 3 veces por modelo si hay saturación temporal (503 / 429)
            for attempt in range(1, 4):
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=[audio_file_upload, prompt],
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            temperature=0.3
                        )
                    )
                    if response.text:
                        return response.text
                except Exception as e:
                    last_error = e
                    err_msg = str(e)
                    # Si es 503 (Servidor saturado) o 429 (Límite de tasa), esperar y reintentar
                    if "503" in err_msg or "UNAVAILABLE" in err_msg or "429" in err_msg:
                        time.sleep(3 * attempt)
                        continue
                    # Si es 404 (Modelo no disponible), pasar al siguiente modelo
                    if "404" in err_msg or "NOT_FOUND" in err_msg:
                        break
                    raise e
        raise last_error

    def analyze_audio(self, audio_path: Path, subject: str = "Clase", date_str: str = "") -> Tuple[str, str]:
        """
        Sube el audio/video a Gemini con extracción de audio automática y reintentos ante saturación 503.
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"El archivo no existe: {audio_path}")

        # 1. Si es video, extraer solo el audio para evitar saturación y acelerar la subida
        proc_path, is_temp = self._extract_audio_if_video(audio_path)

        try:
            # 2. Subir archivo a la File API de Gemini
            audio_file_upload = self.client.files.upload(file=str(proc_path))

            while audio_file_upload.state.name == "PROCESSING":
                time.sleep(2)
                audio_file_upload = self.client.files.get(name=audio_file_upload.name)

            if audio_file_upload.state.name == "FAILED":
                raise RuntimeError(f"Error procesando el archivo en Gemini: {audio_file_upload.error.message}")

            # 3. Formular prompt
            prompt = ANALYSIS_PROMPT_TEMPLATE.format(
                subject=subject,
                date=date_str or time.strftime("%Y-%m-%d")
            )

            # 4. Invocar modelo con reintentos y fallback
            full_text = self._call_gemini_with_resilience(audio_file_upload, prompt)

            # 5. Limpieza del archivo subido en Google Cloud
            try:
                self.client.files.delete(name=audio_file_upload.name)
            except Exception:
                pass

        finally:
            # Eliminar audio temporal si se extrajo de un video
            if is_temp and proc_path.exists():
                proc_path.unlink(missing_ok=True)

        # 6. Extraer texto para TTS y limpiar el Markdown final
        tts_match = re.search(r"## 🎙️ RESUMEN_TTS_INICIO\s*(.*?)\s*## 🎙️ RESUMEN_TTS_FIN", full_text, re.DOTALL)
        if tts_match:
            tts_text = tts_match.group(1).strip()
            clean_markdown = re.sub(r"## 🎙️ RESUMEN_TTS_INICIO.*?## 🎙️ RESUMEN_TTS_FIN", "", full_text, flags=re.DOTALL).strip()
        else:
            tts_text = "Resumen de la clase: " + full_text[:400].replace("#", "")
            clean_markdown = full_text.strip()

        return clean_markdown, tts_text
