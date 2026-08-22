---
name: class-analizer
description: Graba clases virtuales (Google Meet) y genera automáticamente guías de estudio en Markdown, PDF y narración en audio (TTS) utilizando Google Gemini.
---

# ClassAnalizer Skill para OpenClaw

Esta habilidad permite al agente OpenClaw controlar grabaciones de clases y generar resúmenes académicos multiformato.

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
