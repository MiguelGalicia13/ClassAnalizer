---
name: class-analizer
description: Graba clases virtuales (Google Meet) y genera automáticamente guías de estudio en Markdown, PDF y narración en audio (TTS) utilizando Google Gemini o Anthropic Claude.
---

# ClassAnalizer Skill para OpenClaw

**Español** | [English](SKILL_EN.md)

Esta habilidad permite al agente OpenClaw controlar grabaciones de clases y generar resúmenes académicos multiformato.

El proveedor por defecto se configura con `AI_PROVIDER=gemini` o `AI_PROVIDER=anthropic` en `.env`. Claude transcribe primero el audio con `faster-whisper`, por lo que la primera ejecución descargará el modelo local de Whisper.

## Comandos y Triggers Soportados:

1. **Iniciar Grabación:**
   - Prompt de usuario: *"Graba la clase de [Materia]"* o *"Empieza a grabar Sistemas Distribuidos"*.
   - Ejecución: `uv run python openclaw_skill/bridge.py --action start --subject "[Materia]" --json`

2. **Consultar Estado:**
   - Prompt de usuario: *"¿Se está grabando la clase?"* o *"¿Cuánto tiempo llevamos grabando?"*.
   - Ejecución: `uv run python openclaw_skill/bridge.py --action status --json`

3. **Detener y Procesar Guía:**
   - Prompt de usuario: *"Termina la clase"*, *"Detén la grabación y genera la guía"*.
   - Ejecución: `uv run python openclaw_skill/bridge.py --action stop --json`
   - El agente recibe las rutas del archivo Markdown, PDF y audio TTS generado, y puede enviar el resumen directamente al usuario en Telegram/WhatsApp.

Para seleccionar un proveedor, modelo o idioma puntualmente, agrega `--provider anthropic`, `--model claude-sonnet-5` o `--language en` / `--language es` / `--language auto` al comando `stop`.

