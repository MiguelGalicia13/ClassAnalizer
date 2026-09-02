# 🎓 ClassAnalizer

**[Español](README.md)** | **English**

**ClassAnalizer** is an intelligent assistant and recorder for virtual (Google Meet, Zoom, Teams) or in-person classes. It works on Linux (PipeWire/PulseAudio) and Windows 10/11 x64 (WASAPI Loopback). It processes audio with **Google Gemini** or **Anthropic Claude**, automatically generating complete study guides in Markdown, PDF, and audio narrations (TTS).

It includes a modern **Graphical Desktop Application (GUI)**, a **CLI**, and a **Skill for OpenClaw**.

---

## ✨ Key Features

- 🖥️ **Modern Desktop Application:** Visual interface with tabs for **Live Recording** (real-time timer, audio waves, source selector) and **Import Recordings** (drag/select files with automatic `.mp4` video audio extraction).
- 🎙️ **Cross-Platform Capture:** Linux uses PipeWire/PulseAudio and Windows captures system output via WASAPI Loopback, with an option to mix the microphone.
- 🧠 **AI-Powered Analysis:** Native audio processing with Gemini or Claude with local transcription via `faster-whisper`.
- 📄 **Study Guide in Markdown (`.md`):** Executive summary, timeline, in-depth conceptual development, glossary, and exam-style question bank.
- 📕 **Typeset PDF Document (`.pdf`):** Academic styling ready to print or read.
- 🔊 **Narrated Audio Summary (`.mp3`):** Neural text-to-speech synthesis (TTS) to study on the go.
- 🤖 **OpenClaw Skill:** Voice and chat control from Telegram, WhatsApp, or CLI.

---

## 🚀 Quick Start

### Windows Portable (10/11 x64)

Download the Windows ZIP from the **Releases** section, extract it to a folder, and run `ClassAnalizer.bat`. The package includes `uv.exe`: on the first launch, it will automatically download Python 3.12 and dependencies into the user environment, without requiring pre-installed Python or administrator privileges. An internet connection is required during the initial run, along with the Microsoft Edge WebView2 runtime for the interface.

Before starting, configure your API keys locally:

```bat
copy .env.example .env
notepad .env
```

You can also use `ClassAnalizer-Silent.vbs` to launch the GUI without displaying a console window. Recording modes: `meet` captures system audio via WASAPI Loopback, `mic` uses the default microphone, and `both` mixes both audio streams without requiring virtual audio cables (e.g. VB-Cable). On Windows, PDFs are generated with `xhtml2pdf` and `imageio-ffmpeg` provides the multimedia converter included in the portable environment.

For Linux, WeasyPrint and system package installation instructions are retained below.

---

### 1. Install System Dependencies (Linux)

For a native installation on Linux, install audio capture tools, multimedia conversion utilities, PDF rendering libraries, and notification services according to your distribution:

#### Arch Linux, Manjaro, and EndeavourOS

```bash
sudo pacman -Syu --needed python uv ffmpeg pipewire pipewire-pulse wireplumber libnotify pango cairo gdk-pixbuf2 libffi
```

#### Debian, Ubuntu, Linux Mint, and derivatives

```bash
sudo apt update
sudo apt install -y python3 python3-venv curl ffmpeg pipewire pipewire-pulse wireplumber \
  pulseaudio-utils libnotify-bin libcairo2 libpango-1.0-0 libpangoft2-1.0-0 \
  libharfbuzz-subset0 libffi-dev
```

#### Fedora

```bash
sudo dnf install -y python3 curl ffmpeg pipewire pipewire-pulseaudio wireplumber \
  pulseaudio-utils libnotify pango cairo gdk-pixbuf2 libffi
```

If `ffmpeg` is not available in default repositories, enable RPM Fusion first:

```bash
sudo dnf install -y https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
```

#### openSUSE Tumbleweed and Leap

```bash
sudo zypper install -y python3 curl ffmpeg pipewire pipewire-pulseaudio wireplumber \
  pulseaudio-utils libnotify-tools pango cairo gdk-pixbuf libffi
```

---

### 2. Prepare Python and the Project Environment

On distributions where `uv` is not available as a package, install it using the official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

From the repository root, install Python and locked dependencies:

```bash
uv sync
```

Ensure your audio server is running before recording. On Linux, verify with `pactl info` (it should display a PulseAudio or PipeWire server).

---

### 3. Configure AI Provider API Keys

Copy `.env.example` to `.env` and configure `AI_PROVIDER=gemini` or `AI_PROVIDER=anthropic` along with your API key. Obtain keys from [Google AI Studio](https://aistudio.google.com/app/apikey) or [Anthropic Console](https://console.anthropic.com/settings/keys):

```bash
cp .env.example .env
```

For Claude, `faster-whisper` will automatically download the configured `WHISPER_MODEL` (default `large-v3`) during the first analysis. You can use `medium`, `small`, or `base` to reduce disk and memory consumption.

---

### 4. Launch Desktop Application

```bash
uv run classanalizer gui
# or simply:
uv run classanalizer
```

Inside the application you can:
1. **Live Recording:** Enter the subject name, select the audio source, and click *Start Recording*. Monitor elapsed time with the live stopwatch (`00:00:00`) and stop recording when class ends to generate your study guide instantly.
2. **Import Recordings:** Select an audio or video file (`.mp4`, `.mkv`, `.mp3`, etc.). The app extracts audio and sends it to the AI analyzer with one click.
3. **Explore Results:** Open the generated PDF in your system viewer, play back the TTS audio summary, or inspect the Markdown guide.

---

### 5. Install Desktop Launcher on Linux (.desktop)

To integrate ClassAnalizer into your desktop environment (GNOME, KDE, XFCE, Rofi, etc.) and make the `classanalizer` command globally available:

```bash
bash install.sh
```

This script automates:
- Symlink in `~/.local/bin/classanalizer`.
- SVG icon in `~/.local/share/icons/hicolor/scalable/apps/classanalizer.svg`.
- Desktop entry `classanalizer.desktop` in `~/.local/share/applications/`.
- Desktop database and icon cache updates.

---

## 🛠️ Build and Packaging

### Build Distribution Packages (.whl and .tar.gz)
```bash
uv build
```
Artifacts will be generated in `dist/`.

### Native Installation on Arch Linux (PKGBUILD)
```bash
makepkg -si
```

---

## 💻 Terminal Usage (CLI)

- **Record a class in the background:**
  ```bash
  uv run classanalizer start "Computer_Networks"
  ```
- **Real-time monitor & stopwatch:**
  ```bash
  uv run classanalizer watch
  ```
- **Stop recording and generate study guide:**
  ```bash
  uv run classanalizer stop
  ```
- **Analyze an existing media file via CLI:**
  ```bash
  uv run classanalizer analyze /path/to/class.mp4 --subject "Systems_Theory"
  ```
- **Analyze with Anthropic Claude:**
  ```bash
  uv run classanalizer analyze /path/to/class.mp4 \
    --provider anthropic --model claude-sonnet-5 --subject "Systems_Theory"
  ```
- **Validate API key and list available models:**
  ```bash
  uv run classanalizer validate --provider anthropic
  ```

---

## 🤖 OpenClaw Integration

See the [`openclaw_skill/`](openclaw_skill/) directory to use ClassAnalizer with your personal AI agent.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
