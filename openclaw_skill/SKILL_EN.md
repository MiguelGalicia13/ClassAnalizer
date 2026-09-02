---
name: class-analizer
description: Records virtual classes (Google Meet, Zoom, Teams) and automatically generates study guides in Markdown, PDF, and audio narration (TTS) using Google Gemini or Anthropic Claude.
---

# ClassAnalizer Skill for OpenClaw

**[Español](SKILL.md)** | **English**

This skill enables the OpenClaw agent to control class recordings and generate multi-format academic study summaries.

The default provider is configured via `AI_PROVIDER=gemini` or `AI_PROVIDER=anthropic` in `.env`. When using Claude, audio is transcribed first using local `faster-whisper`, so the first run will download the local Whisper model.

## Supported Commands and Triggers:

1. **Start Recording:**
   - User prompt: *"Record my [Subject] class"* or *"Start recording Distributed Systems"*.
   - Execution: `uv run python openclaw_skill/bridge.py --action start --subject "[Subject]" --json`

2. **Check Status:**
   - User prompt: *"Is the class recording?"* or *"How long have we been recording?"*.
   - Execution: `uv run python openclaw_skill/bridge.py --action status --json`

3. **Stop and Process Study Guide:**
   - User prompt: *"Class is over"*, *"Stop recording and generate the study guide"*.
   - Execution: `uv run python openclaw_skill/bridge.py --action stop --json`
   - The agent receives the paths to the generated Markdown file, PDF document, and TTS audio narration, and can deliver the summary directly to the user via Telegram/WhatsApp/Discord.

To specify a provider, model, or output language on demand, append `--provider anthropic`, `--model claude-sonnet-5`, or `--language en` / `--language es` / `--language auto` to the `stop` command.

