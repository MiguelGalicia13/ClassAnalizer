from typing import Any, Optional

from classanalizer.base_analyzer import BaseAnalyzer
from classanalizer.config import AI_PROVIDER


GEMINI_FALLBACK_MODELS = [
    {"id": "gemini-3.7-flash", "name": "Gemini 3.7 Flash (Recomendado)"},
    {"id": "gemini-3.6-flash", "name": "Gemini 3.6 Flash"},
    {"id": "gemini-3.5-flash", "name": "Gemini 3.5 Flash"},
    {"id": "gemini-flash-latest", "name": "Gemini Flash Latest"},
]

ANTHROPIC_FALLBACK_MODELS = [
    {"id": "claude-sonnet-5", "name": "Claude Sonnet 5 (Recomendado)"},
    {"id": "claude-opus-5", "name": "Claude Opus 5 (Máxima capacidad)"},
    {"id": "claude-haiku-4-5-20251001", "name": "Claude Haiku 4.5 (Rápido)"},
]


def normalize_provider(provider: Optional[str] = None) -> str:
    selected = (provider or AI_PROVIDER).lower().strip()
    aliases = {"google": "gemini", "claude": "anthropic"}
    selected = aliases.get(selected, selected)
    if selected not in {"gemini", "anthropic"}:
        raise ValueError(
            f"Proveedor de IA no reconocido: '{selected}'. "
            "Usa 'gemini' o 'anthropic'."
        )
    return selected


def create_analyzer(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> BaseAnalyzer:
    """Crea el analizador correspondiente al proveedor seleccionado."""
    selected = normalize_provider(provider)
    if selected == "anthropic":
        from classanalizer.claude_analyzer import ClaudeAnalyzer

        return ClaudeAnalyzer(api_key=api_key, model=model)

    from classanalizer.analyzer import GeminiAnalyzer

    return GeminiAnalyzer(api_key=api_key, model=model)


def validate_provider_key(
    provider: str,
    api_key: Optional[str] = None,
) -> tuple[bool, str]:
    """Valida una clave y devuelve (válida, mensaje)."""
    try:
        analyzer = create_analyzer(provider=provider, api_key=api_key)
        if analyzer.validate_api_key():
            return True, f"API key de {analyzer.provider_name} validada correctamente."
        return False, f"API key de {analyzer.provider_name} inválida o sin permisos."
    except ValueError as exc:
        return False, str(exc)
    except Exception as exc:
        return False, f"Error validando API key: {exc}"


def list_models_for_provider(
    provider: str,
    api_key: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Lista los modelos accesibles o devuelve opciones estáticas como fallback."""
    analyzer = create_analyzer(provider=provider, api_key=api_key)
    return analyzer.list_available_models()


def fallback_models_for_provider(provider: str) -> list[dict[str, str]]:
    """Devuelve modelos conocidos para mostrar cuando no hay conexión o API key."""
    selected = normalize_provider(provider)
    models = ANTHROPIC_FALLBACK_MODELS if selected == "anthropic" else GEMINI_FALLBACK_MODELS
    return [model.copy() for model in models]
