from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional


class BaseAnalyzer(ABC):
    """Interfaz común para los proveedores de análisis de clases."""

    @abstractmethod
    def analyze_audio(
        self,
        audio_path: Path,
        subject: str = "Clase",
        date_str: str = "",
        model: Optional[str] = None,
        language: Optional[str] = "auto",
    ) -> tuple[str, str]:
        """Analiza audio/video y devuelve (guía Markdown, resumen para TTS)."""

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Verifica las credenciales del proveedor sin generar contenido."""

    @abstractmethod
    def list_available_models(self) -> list[dict[str, Any]]:
        """Devuelve los modelos accesibles para las credenciales configuradas."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Devuelve el nombre legible del proveedor."""
