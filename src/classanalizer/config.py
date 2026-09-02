import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from classanalizer.platform_utils import get_default_output_dir, get_session_file_path

# Cargar variables desde .env local o raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Modelo predeterminado actualizado a gemini-3.6-flash
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

# --- Proveedor y modelos de IA ---
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").strip().lower()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5")

# Modelo Whisper local usado para proveedores sin entrada de audio nativa
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "large-v3")

_raw_output_dir = os.getenv("OUTPUT_DIR")
if not _raw_output_dir:
    _raw_output_dir = str(get_default_output_dir())
OUTPUT_DIR = Path(os.path.expanduser(_raw_output_dir))

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "auto").strip().lower()

TTS_VOICE_ES = os.getenv("TTS_VOICE_ES", os.getenv("TTS_VOICE", "es-MX-JorgeNeural"))
TTS_VOICE_EN = os.getenv("TTS_VOICE_EN", "en-US-JennyNeural")
TTS_VOICE = TTS_VOICE_ES


def get_tts_voice(language: Optional[str] = None, text: Optional[str] = None) -> str:
    """Selecciona la voz de TTS adecuada según el idioma o el texto analizado."""
    lang = (language or DEFAULT_LANGUAGE or "auto").strip().lower()
    if lang.startswith("en"):
        return TTS_VOICE_EN
    if lang.startswith("es"):
        return TTS_VOICE_ES

    # Si es auto y se proporciona texto, hacemos una detección simple por vocabulario común
    if text:
        text_lower = text.lower()
        en_indicators = [" the ", " and ", " in this lecture ", " we discussed ", " key takeaways ", " summary "]
        es_indicators = [" la ", " el ", " en esta clase ", " se discutió ", " puntos clave ", " resumen "]
        en_score = sum(1 for w in en_indicators if w in text_lower)
        es_score = sum(1 for w in es_indicators if w in text_lower)
        if en_score > es_score:
            return TTS_VOICE_EN

    return TTS_VOICE_ES


# Ruta para almacenar archivos de estado de sesión
SESSION_FILE = get_session_file_path()
