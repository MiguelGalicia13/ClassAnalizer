import json
import threading
from pathlib import Path
from typing import Optional, Dict, Any

import webview

from classanalizer.recorder import AudioRecorder
from classanalizer.analyzer_factory import (
    fallback_models_for_provider,
    list_models_for_provider,
    normalize_provider,
    validate_provider_key,
    create_analyzer,
)
from classanalizer.exporter import Exporter
from classanalizer.config import (
    AI_PROVIDER,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OUTPUT_DIR,
    TTS_VOICE,
)
from classanalizer.platform import get_gui_backend, open_in_system_viewer


def get_configured_api_key(provider: str) -> str:
    """Devuelve únicamente la clave configurada para un proveedor."""
    return ANTHROPIC_API_KEY if provider == "anthropic" else GEMINI_API_KEY


def get_configured_model(provider: str) -> str:
    """Devuelve el modelo predeterminado del proveedor."""
    if provider == "anthropic":
        return ANTHROPIC_MODEL or "claude-sonnet-5"
    return GEMINI_MODEL or "gemini-3.7-flash"


def get_models_for_ui(provider: str, api_key: str) -> list[dict[str, Any]]:
    """Obtiene modelos remotos y conserva opciones conocidas si falla la red."""
    if not api_key:
        return fallback_models_for_provider(provider)
    try:
        return list_models_for_provider(provider, api_key=api_key)
    except Exception:
        return fallback_models_for_provider(provider)


class DesktopBridgeApi:
    def __init__(self):
        self._window: Optional[webview.Window] = None

    def set_window(self, window: webview.Window):
        self._window = window

    def get_initial_state(self) -> Dict[str, Any]:
        """Devuelve el estado inicial del sistema al cargar la UI."""
        session = AudioRecorder.get_session_info()
        provider = normalize_provider(AI_PROVIDER)
        provider_key = get_configured_api_key(provider)
        model = get_configured_model(provider)
        available_models = get_models_for_ui(provider, provider_key)
        return {
            "provider": provider,
            "has_api_key": bool(provider_key),
            "api_key_configured": {
                "gemini": bool(GEMINI_API_KEY),
                "anthropic": bool(ANTHROPIC_API_KEY),
            },
            "model": model,
            "available_models": available_models,
            "output_dir": str(OUTPUT_DIR),
            "is_recording": AudioRecorder.is_recording(),
            "active_session": session
        }

    def get_provider_state(
        self,
        provider: str,
        api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Devuelve modelos y estado de credenciales para el proveedor elegido."""
        selected_provider = normalize_provider(provider)
        configured_key = api_key.strip() if api_key and api_key.strip() else get_configured_api_key(selected_provider)
        return {
            "provider": selected_provider,
            "has_api_key": bool(configured_key),
            "model": get_configured_model(selected_provider),
            "available_models": get_models_for_ui(selected_provider, configured_key),
        }

    def validate_api_key(self, provider: str, api_key: str) -> Dict[str, Any]:
        """Valida una API key y retorna los modelos accesibles sin exponerla."""
        if not api_key or not api_key.strip():
            return {"is_valid": False, "message": "Ingresa una API key para validarla."}

        selected_provider = normalize_provider(provider)
        is_valid, message = validate_provider_key(selected_provider, api_key.strip())
        result: Dict[str, Any] = {"is_valid": is_valid, "message": message}
        if is_valid:
            try:
                models = list_models_for_provider(selected_provider, api_key=api_key.strip())
                result["models"] = [
                    {"id": model["id"], "name": model["name"]}
                    for model in models
                ]
            except Exception:
                result["models"] = fallback_models_for_provider(selected_provider)
        return result

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

    def run_analysis(
        self,
        file_path: str,
        subject: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Procesa un archivo con el proveedor y modelo seleccionados."""
        try:
            path_obj = Path(file_path).resolve()
            if not path_obj.exists():
                return {"status": "error", "message": f"El archivo no existe: {file_path}"}

            safe_subject = "".join(c for c in subject if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
            if not safe_subject:
                safe_subject = path_obj.stem

            out_dir = OUTPUT_DIR / safe_subject / time_now_date()
            out_dir.mkdir(parents=True, exist_ok=True)

            selected_provider = normalize_provider(provider)
            analyzer = create_analyzer(
                provider=selected_provider,
                api_key=api_key.strip() if api_key and api_key.strip() else None,
                model=model,
            )
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
        return open_in_system_viewer(target_path)


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
    webview.start(gui=get_gui_backend(), debug=False)


if __name__ == "__main__":
    launch_gui()
