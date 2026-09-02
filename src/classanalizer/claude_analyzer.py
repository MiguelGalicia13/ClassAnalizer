import re
import time
from pathlib import Path
from typing import Any, Optional

import anthropic

from classanalizer.base_analyzer import BaseAnalyzer
from classanalizer.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from classanalizer.prompts import get_prompts
from classanalizer.transcriber import Transcriber


class ClaudeAnalyzer(BaseAnalyzer):
    """Analiza clases con Claude después de transcribirlas localmente."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError(
                "No se encontró ANTHROPIC_API_KEY. Configúrala en el archivo .env o en tus variables de entorno.\n"
                "Puedes obtener tu clave en: https://console.anthropic.com/settings/keys"
            )

        self.default_model = model or ANTHROPIC_MODEL or "claude-sonnet-5"
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self._transcriber = Transcriber()

    @property
    def provider_name(self) -> str:
        return "Anthropic Claude"

    def validate_api_key(self) -> bool:
        """Valida la clave con Models API sin consumir tokens de inferencia."""
        try:
            self.client.models.list(limit=1)
            return True
        except (anthropic.AuthenticationError, anthropic.PermissionDeniedError):
            return False
        except Exception:
            return False

    def list_available_models(self) -> list[dict[str, Any]]:
        """Consulta los modelos disponibles para la clave configurada."""
        try:
            result = self.client.models.list(limit=100)
            return [
                {
                    "id": model.id,
                    "name": model.display_name,
                    "max_input_tokens": model.max_input_tokens,
                    "max_output_tokens": model.max_tokens,
                }
                for model in result.data
            ]
        except Exception as exc:
            raise RuntimeError(f"Error obteniendo modelos de Anthropic: {exc}") from exc

    def _call_claude_with_resilience(
        self,
        transcript: str,
        prompt: str,
        primary_model: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Invoca Claude con reintentos ante rate limits y saturación."""
        candidate_models = [
            primary_model,
            "claude-sonnet-5",
            "claude-opus-5",
            "claude-haiku-4-5-20251001",
        ]
        seen: set[str] = set()
        models_to_try = [
            model for model in candidate_models
            if not (model in seen or seen.add(model))
        ]

        user_content = (
            "A continuación se encuentra la transcripción completa de una clase grabada / The following is the full lecture transcript:\n\n"
            f"---\n{transcript}\n---\n\n{prompt}"
        )

        last_error: Optional[Exception] = None
        for model_name in models_to_try:
            for attempt in range(1, 4):
                try:
                    response = self.client.messages.create(
                        model=model_name,
                        max_tokens=8192,
                        system=system_prompt or "You are an elite academic assistant.",
                        messages=[{"role": "user", "content": user_content}],
                        temperature=0.3,
                    )
                    response_text = "".join(
                        block.text
                        for block in response.content
                        if block.type == "text"
                    ).strip()
                    if response_text:
                        return response_text
                    last_error = RuntimeError(
                        f"Claude no devolvió texto para el modelo {model_name}."
                    )
                except anthropic.RateLimitError as exc:
                    last_error = exc
                    time.sleep(3 * attempt)
                except anthropic.NotFoundError as exc:
                    last_error = exc
                    break
                except anthropic.APIStatusError as exc:
                    last_error = exc
                    if exc.status_code in (429, 503, 529):
                        time.sleep(3 * attempt)
                        continue
                    raise

        raise last_error or RuntimeError(
            "No se pudo obtener respuesta de ningún modelo Claude."
        )

    def analyze_audio(
        self,
        audio_path: Path,
        subject: str = "Clase",
        date_str: str = "",
        model: Optional[str] = None,
        language: Optional[str] = "auto",
    ) -> tuple[str, str]:
        """Ejecuta el pipeline audio → Whisper → Claude → entregables de texto."""
        if not audio_path.exists():
            raise FileNotFoundError(f"El archivo no existe: {audio_path}")

        selected_model = model or self.default_model
        transcript = self._transcriber.transcribe(audio_path, language=language)
        if len(transcript.strip()) < 50:
            raise RuntimeError(
                "La transcripción está vacía o es demasiado corta. "
                "Verifica que el archivo contenga voz legible."
            )

        system_prompt, prompt = get_prompts(
            subject=subject,
            date_str=date_str or time.strftime("%Y-%m-%d"),
            language=language or "auto",
        )
        full_text = self._call_claude_with_resilience(
            transcript,
            prompt,
            primary_model=selected_model,
            system_prompt=system_prompt,
        )

        tts_match = re.search(
            r"## 🎙️ RESUMEN_TTS_INICIO\s*(.*?)\s*## 🎙️ RESUMEN_TTS_FIN",
            full_text,
            re.DOTALL,
        )
        if tts_match:
            tts_text = tts_match.group(1).strip()
            clean_markdown = re.sub(
                r"## 🎙️ RESUMEN_TTS_INICIO.*?## 🎙️ RESUMEN_TTS_FIN",
                "",
                full_text,
                flags=re.DOTALL,
            ).strip()
        else:
            tts_text = "Resumen de la clase: " + full_text[:400].replace("#", "")
            clean_markdown = full_text.strip()

        return clean_markdown, tts_text
