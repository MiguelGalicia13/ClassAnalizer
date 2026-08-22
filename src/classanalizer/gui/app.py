import json
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional, Dict, Any

import webview

from classanalizer.recorder import AudioRecorder
from classanalizer.analyzer import GeminiAnalyzer
from classanalizer.exporter import Exporter
from classanalizer.config import OUTPUT_DIR, TTS_VOICE, GEMINI_MODEL, GEMINI_API_KEY


class DesktopBridgeApi:
    def __init__(self):
        self._window: Optional[webview.Window] = None

    def set_window(self, window: webview.Window):
        self._window = window

    def get_initial_state(self) -> Dict[str, Any]:
        """Devuelve el estado inicial del sistema al cargar la UI."""
        session = AudioRecorder.get_session_info()
        return {
            "has_api_key": bool(GEMINI_API_KEY),
            "model": GEMINI_MODEL or "gemini-3.7-flash",
            "available_models": [
                {"id": "gemini-3.7-flash", "name": "Gemini 3.7 Flash (Recomendado / Más Reciente)"},
                {"id": "gemini-3.6-flash", "name": "Gemini 3.6 Flash"},
                {"id": "gemini-3.5-flash", "name": "Gemini 3.5 Flash"},
                {"id": "gemini-flash-latest", "name": "Gemini Flash Latest"}
            ],
            "output_dir": str(OUTPUT_DIR),
            "is_recording": AudioRecorder.is_recording(),
            "active_session": session
        }

    def select_file_dialog(self) -> Dict[str, Any]:
        """Abre un diálogo nativo de Linux para seleccionar un archivo de audio o video."""
        if not self._window:
            return {"status": "error", "message": "Ventana no inicializada"}

        file_types = (
            "Audios y Videos (*.mp3;*.wav;*.m4a;*.mp4;*.mkv;*.webm;*.ogg;*.aac;*.flac)",
            "Todos los archivos (*.*)"
        )
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types
        )

        if result and len(result) > 0:
            selected_path = Path(result[0])
            size_mb = selected_path.stat().st_size / (1024 * 1024)
            is_video = selected_path.suffix.lower() in {".mp4", ".mkv", ".mov", ".avi", ".webm"}
            return {
                "status": "success",
                "path": str(selected_path),
                "filename": selected_path.name,
                "size_str": f"{size_mb:.2f} MB" if size_mb >= 1 else f"{size_mb * 1024:.1f} KB",
                "is_video": is_video,
                "suggested_subject": selected_path.stem.replace("_", " ").replace("-", " ").title()
            }
        return {"status": "cancelled"}

    def start_recording(self, subject: str, source: str) -> Dict[str, Any]:
        try:
            session = AudioRecorder.start_recording(subject=subject, source=source)
            return {"status": "success", "session": session}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_recording_status(self) -> Dict[str, Any]:
        session = AudioRecorder.get_session_info()
        return {
            "is_recording": AudioRecorder.is_recording(),
            "session": session
        }

    def stop_recording_and_process(self) -> Dict[str, Any]:
        try:
            session = AudioRecorder.stop_recording()
            return {"status": "success", "session": session}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def run_analysis(self, file_path: str, subject: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Procesa un archivo de audio/video con el modelo Flash seleccionado."""
        try:
            path_obj = Path(file_path).resolve()
            if not path_obj.exists():
                return {"status": "error", "message": f"El archivo no existe: {file_path}"}

            safe_subject = "".join(c for c in subject if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
            if not safe_subject:
                safe_subject = path_obj.stem

            out_dir = OUTPUT_DIR / safe_subject / time_now_date()
            out_dir.mkdir(parents=True, exist_ok=True)

            analyzer = GeminiAnalyzer()
            markdown_text, tts_text = analyzer.analyze_audio(path_obj, subject=subject, model=model)

            md_file = out_dir / "guia_estudio.md"
            pdf_file = out_dir / "guia_estudio.pdf"
            tts_file = out_dir / "resumen_audio.mp3"

            Exporter.export_markdown(markdown_text, md_file)
            Exporter.export_pdf(markdown_text, pdf_file)
            Exporter.export_tts_audio(tts_text, tts_file, voice=TTS_VOICE)

            return {
                "status": "success",
                "artifacts": {
                    "markdown_file": str(md_file),
                    "markdown_content": markdown_text,
                    "pdf_file": str(pdf_file),
                    "tts_audio_file": str(tts_file),
                    "tts_text": tts_text,
                    "output_dir": str(out_dir)
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def open_path_in_system(self, target_path: str):
        """Abre un archivo o carpeta en el visor predeterminado del sistema operativo."""
        try:
            subprocess.run(["xdg-open", target_path], check=False)
            return {"status": "success"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


def time_now_date() -> str:
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d")


def launch_gui():
    api = DesktopBridgeApi()
    html_path = Path(__file__).resolve().parent / "templates" / "index.html"

    window = webview.create_window(
        title="🎓 ClassAnalizer — Grabador Inteligente y Asistente de Clases",
        url=str(html_path),
        js_api=api,
        width=1120,
        height=820,
        min_size=(900, 650),
        background_color="#0f172a"
    )
    api.set_window(window)
    webview.start(gui="qt", debug=False)


if __name__ == "__main__":
    launch_gui()
