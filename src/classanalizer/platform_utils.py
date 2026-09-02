"""Abstracciones pequeñas para mantener la aplicación multiplataforma."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


IS_WINDOWS = sys.platform == "win32"


def is_process_alive(pid: int) -> bool:
    """Comprueba si un proceso sigue activo de forma portable."""
    if IS_WINDOWS:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel32.GetExitCodeProcess.restype = wintypes.BOOL
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL

        process_query_limited_information = 0x1000
        handle = kernel32.OpenProcess(process_query_limited_information, False, int(pid))
        if not handle:
            return False
        exit_code = wintypes.DWORD()
        try:
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return False
            return exit_code.value == 259  # STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)

    try:
        os.kill(pid, 0)
        return True
    except PermissionError:
        return True
    except ProcessLookupError:
        return False
    except OSError:
        return False


def get_ffmpeg_binary() -> str:
    """Devuelve un ffmpeg usable, priorizando el sistema en Linux."""
    # En Linux se necesita la compilación del sistema para conservar la
    # entrada PulseAudio/PipeWire. En Windows imageio-ffmpeg aporta el binario.
    if not IS_WINDOWS:
        system_ffmpeg = shutil.which("ffmpeg")
        if system_ffmpeg:
            return system_ffmpeg

    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass

    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    raise FileNotFoundError(
        "No se encontró ffmpeg. En Linux instálalo con el gestor de paquetes; "
        "en Windows ejecuta la distribución portable para descargarlo automáticamente."
    )


def get_session_file_path() -> Path:
    """Ruta del estado de sesión en el directorio temporal del usuario."""
    return Path(tempfile.gettempdir()) / "classanalizer_session.json"


def get_default_output_dir() -> Path:
    """Directorio de resultados por defecto según el sistema operativo."""
    return Path.home() / "Clases"


def open_in_system_viewer(target_path: str | Path) -> dict[str, str]:
    """Abre un archivo o carpeta con la aplicación predeterminada del sistema."""
    try:
        if IS_WINDOWS:
            os.startfile(os.fspath(target_path))  # type: ignore[attr-defined]
        else:
            subprocess.run(["xdg-open", os.fspath(target_path)], check=False)
        return {"status": "success"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def send_desktop_notification(
    title: str, message: str, urgency: str = "normal"
) -> None:
    """Envía una notificación nativa cuando el entorno lo permite."""
    if IS_WINDOWS:
        try:
            from win11toast import toast

            toast(title, message, app_id="ClassAnalizer")
        except Exception:
            pass
        return

    try:
        subprocess.run(
            ["notify-send", "-a", "ClassAnalizer", "-u", urgency, title, message],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except Exception:
        pass


def get_gui_backend() -> str:
    """Selecciona Qt en Linux y EdgeChromium/WebView2 en Windows."""
    return "edgechromium" if IS_WINDOWS else "qt"
