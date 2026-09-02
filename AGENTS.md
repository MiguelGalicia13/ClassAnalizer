# Repository Guidelines

## Project Structure & Module Organization

- `src/classanalizer/` contains the application package. `cli.py` defines the command-line interface, `recorder.py` manages PipeWire/PulseAudio capture, `analyzer.py` integrates Gemini, `claude_analyzer.py` integrates Anthropic through local Whisper transcription, and `exporter.py` creates Markdown, PDF, and TTS outputs.
- `base_analyzer.py`, `analyzer_factory.py`, and `transcriber.py` provide the shared provider interface, provider selection, and Claude STT pipeline.
- `src/classanalizer/gui/` contains the PyQt6 desktop application and its HTML template.
- `openclaw_skill/` provides the JSON bridge and OpenClaw skill metadata.
- `assets/`, `classanalizer.desktop`, `install.sh`, and `PKGBUILD` support Linux desktop installation and Arch packaging.
- `README.md` documents user-facing workflows. Generated recordings and guides belong under the configured `OUTPUT_DIR`, not in the repository.

## Build, Test, and Development Commands

Use Python 3.14 and `uv`:

```bash
uv sync                         # Create/update the development environment
uv run classanalizer            # Launch the GUI
uv run classanalizer --help     # Inspect CLI commands
uv run classanalizer analyze path/to/class.mp4 --subject "Networks"
uv run classanalizer validate --provider anthropic  # Validate a provider key and list models
uv build                        # Build distributable package artifacts
bash install.sh                 # Install the desktop launcher locally on Arch/Linux
```

Audio/video workflows require system tools such as `ffmpeg` and PipeWire/PulseAudio; desktop notifications use optional `notify-send`.

## Coding Style & Naming Conventions

Follow standard Python style: four-space indentation, `snake_case` for functions and variables, `PascalCase` for classes, and type hints for public interfaces. Keep user-facing CLI and GUI text consistent with the existing Spanish-language UI. Place reusable application logic in `src/classanalizer/`; keep CLI parsing and integration adapters thin. No formatter or linter is configured, so review changes for PEP 8 consistency before submitting.

## Testing Guidelines

No test framework or test directory is currently committed. For changes, at minimum run `uv run classanalizer --help` and exercise the affected CLI/GUI path with a representative local audio file. Avoid live Gemini or Anthropic calls in routine checks; use isolated mocks when adding tests for API, transcription, or exporter behavior. Do not commit recordings, generated PDFs/MP3s, credentials, or `.env` files.

## Commit & Pull Request Guidelines

Recent commits use short, imperative-style Conventional Commit prefixes such as `feat:`. Follow that pattern (`feat:`, `fix:`, `docs:`, `refactor:`) with a concise Spanish or English summary. Pull requests should explain the user-visible change, list verification commands, note Linux/system dependencies, and include screenshots for GUI changes. Call out changes to environment variables, Gemini/Claude models, Whisper settings, packaging, or generated output formats.
