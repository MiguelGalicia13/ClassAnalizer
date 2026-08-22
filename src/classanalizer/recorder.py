import json
import os
import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from classanalizer.config import SESSION_FILE, OUTPUT_DIR


class AudioRecorder:
    """Gestiona la grabación de audio en segundo plano usando ffmpeg y PulseAudio/PipeWire."""

    @staticmethod
    def is_recording() -> bool:
        if not SESSION_FILE.exists():
            return False
        try:
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            pid = data.get("pid")
            if not pid:
                return False
            # Comprobar si el proceso sigue vivo
            os.kill(pid, 0)
            return True
        except (OSError, ValueError, json.JSONDecodeError):
            if SESSION_FILE.exists():
                SESSION_FILE.unlink(missing_ok=True)
            return False

    @staticmethod
    def get_session_info() -> Optional[Dict[str, Any]]:
        if not AudioRecorder.is_recording():
            return None
        try:
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            start_time = data.get("start_timestamp", time.time())
            data["elapsed_seconds"] = int(time.time() - start_time)
            return data
        except Exception:
            return None

    @staticmethod
    def start_recording(subject: str = "Clase", source: str = "meet") -> Dict[str, Any]:
        """
        Inicia la grabación en segundo plano.
        source:
          - 'meet': Solo audio del sistema/Google Meet (@DEFAULT_SINK@.monitor)
          - 'mic': Solo micrófono (@DEFAULT_SOURCE@)
          - 'both': Mezcla de Meet + Mic
        """
        if AudioRecorder.is_recording():
            session = AudioRecorder.get_session_info()
            raise RuntimeError(f"Ya hay una grabación en curso para '{session.get('subject')}' (PID {session.get('pid')})")

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H%M%S")
        safe_subject = "".join(c for c in subject if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
        if not safe_subject:
            safe_subject = "Clase"

        # Directorio de salida
        class_dir = OUTPUT_DIR / safe_subject / date_str
        class_dir.mkdir(parents=True, exist_ok=True)

        audio_file = class_dir / f"grabacion_{time_str}.mp3"
        log_file = class_dir / f"ffmpeg_{time_str}.log"

        cmd = ["ffmpeg", "-y", "-nostdin", "-loglevel", "warning"]

        if source == "meet":
            cmd.extend(["-f", "pulse", "-i", "@DEFAULT_SINK@.monitor"])
        elif source == "mic":
            cmd.extend(["-f", "pulse", "-i", "@DEFAULT_SOURCE@"])
        else:  # both
            cmd.extend([
                "-f", "pulse", "-i", "@DEFAULT_SINK@.monitor",
                "-f", "pulse", "-i", "@DEFAULT_SOURCE@",
                "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=longest[aout]",
                "-map", "[aout]"
            ])

        # Formato de audio comprimido optimizado para voz
        cmd.extend(["-c:a", "libmp3lame", "-b:a", "96k", "-ar", "44100", str(audio_file)])

        # Lanzar proceso en segundo plano desconectado de stdin
        log_handle = open(log_file, "w", encoding="utf-8")
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

        session_data = {
            "pid": process.pid,
            "subject": subject,
            "safe_subject": safe_subject,
            "source": source,
            "date": date_str,
            "start_timestamp": time.time(),
            "start_iso": now.isoformat(),
            "audio_file": str(audio_file),
            "output_dir": str(class_dir),
            "log_file": str(log_file)
        }

        SESSION_FILE.write_text(json.dumps(session_data, indent=2), encoding="utf-8")
        return session_data

    @staticmethod
    def stop_recording() -> Dict[str, Any]:
        """Detiene la grabación de forma limpia y devuelve la información de la sesión."""
        if not SESSION_FILE.exists():
            raise RuntimeError("No hay ninguna grabación activa para detener.")

        try:
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            SESSION_FILE.unlink(missing_ok=True)
            raise RuntimeError(f"Error leyendo archivo de sesión: {e}")

        pid = data.get("pid")
        if pid:
            try:
                # Enviar SIGINT para que ffmpeg cierre el archivo MP3 correctamente
                os.kill(pid, signal.SIGINT)
                # Esperar hasta 5 segundos a que termine
                for _ in range(50):
                    time.sleep(0.1)
                    try:
                        os.kill(pid, 0)
                    except OSError:
                        break
                else:
                    # Si no termina con SIGINT, forzar SIGTERM
                    os.kill(pid, signal.SIGTERM)
            except OSError:
                pass  # Ya terminó

        SESSION_FILE.unlink(missing_ok=True)
        start_time = data.get("start_timestamp", time.time())
        data["duration_seconds"] = int(time.time() - start_time)
        return data
