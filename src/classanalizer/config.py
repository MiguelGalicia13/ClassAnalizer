import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables desde .env local o raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Modelo predeterminado actualizado a gemini-3.6-flash
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

_raw_output_dir = os.getenv("OUTPUT_DIR", "~/Clases")
OUTPUT_DIR = Path(os.path.expanduser(_raw_output_dir))

TTS_VOICE = os.getenv("TTS_VOICE", "es-MX-JorgeNeural")

# Ruta para almacenar archivos de estado de sesión
SESSION_FILE = Path("/tmp/classanalizer_session.json")
