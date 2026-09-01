# 🎓 ClassAnalizer

**ClassAnalizer** es un asistente y grabador inteligente para clases virtuales (Google Meet, Zoom, Teams) o presenciales en Linux (PipeWire/PulseAudio). Procesa el audio directamente con la API multimodal de **Google Gemini**, generando automáticamente guías de estudio completas en Markdown, PDF y narraciones en audio (TTS).

Cuenta tanto con una **Aplicación de Escritorio Gráfica (GUI)** moderna como con una **CLI** y una **Skill para OpenClaw**.

---

## ✨ Características Principales

- 🖥️ **Aplicación de Escritorio Moderna:** Interfaz visual con pestañas para **Grabar en Vivo** (cronómetro en tiempo real, ondas de audio, selector de fuente) o **Importar Grabaciones** (arrastrar/seleccionar archivos con optimización automática de videos `.mp4`).
- 🎙️ **Captura del Sistema en Linux:** Graba la salida de audio de Google Meet (`@DEFAULT_SINK@.monitor`) mezclada con tu micrófono físico (`@DEFAULT_SOURCE@`) en segundo plano sin congelar la app.
- 🧠 **Análisis con Gemini:** Sube el audio a la File API con reintentos exponenciales automáticos y fallback ante saturación del servidor (503).
- 📄 **Guía de Estudio en Markdown (`.md`):** Resumen ejecutivo, cronología, desarrollo conceptual a fondo, glosario y banco de preguntas tipo examen.
- 📕 **Documento PDF Maquetado (`.pdf`):** Estilo académico listo para imprimir o leer.
- 🔊 **Resumen Narrado en Audio (`.mp3`):** Síntesis de voz neuronal (TTS en español) para repasar escuchando.
- 🤖 **Skill para OpenClaw:** Control por voz y chat desde Telegram, WhatsApp o CLI.

---

## 🚀 Inicio Rápido

### 1. Instalar dependencias del sistema

ClassAnalizer está orientado a Linux. Instala las herramientas de captura de audio, conversión multimedia, renderizado de PDF y notificaciones según tu distribución.

#### Arch Linux, Manjaro y EndeavourOS

```bash
sudo pacman -Syu --needed python uv ffmpeg pipewire pipewire-pulse wireplumber libnotify pango cairo gdk-pixbuf2 libffi
```

#### Debian, Ubuntu, Linux Mint y derivados

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

Si `ffmpeg` no está disponible en los repositorios habilitados, instala primero RPM Fusion y repite el comando:

```bash
sudo dnf install -y https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
```

#### openSUSE Tumbleweed y Leap

```bash
sudo zypper install -y python3 curl ffmpeg pipewire pipewire-pulseaudio wireplumber \
  pulseaudio-utils libnotify-tools pango cairo gdk-pixbuf libffi
```

En otras distribuciones, instala los equivalentes de `ffmpeg`, `pipewire` o `pulseaudio`, `wireplumber`, `pango` y `libffi` con su gestor de paquetes.

### 2. Preparar Python y el entorno del proyecto

En distribuciones donde `uv` no esté disponible como paquete, instálalo con su instalador oficial:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Desde la raíz del repositorio, instala Python 3.14 y las dependencias bloqueadas:

```bash
uv python install 3.14
uv sync
```

Comprueba que el servidor de audio esté activo antes de grabar. Puedes verificarlo con `pactl info`; debe mostrar un servidor PulseAudio o PulseAudio sobre PipeWire.

### 3. Configurar tu API Key de Gemini

Copia `.env.example` a `.env` y coloca tu clave gratuita de [Google AI Studio](https://aistudio.google.com/app/apikey):

```bash
cp .env.example .env
```

### 4. Lanzar la Aplicación de Escritorio

```bash
uv run classanalizer gui
# o simplemente:
uv run classanalizer
```

Dentro de la aplicación podrás:
1. **Grabar en Vivo:** Asigna nombre a la materia, elige la fuente de audio y pulsa *Iniciar Grabación*. Verás el cronómetro en tiempo real (`00:00:00`) y podrás detenerla cuando termine la clase para generar tu guía al instante.
2. **Importar Grabación:** Selecciona un archivo de audio o video (`.mp4`, `.mkv`, `.mp3`, etc.). La app optimizará el video extrayendo el audio y lo enviará a Gemini con un solo clic.
3. **Explorar Resultados:** Abre el PDF directamente en tu visor, reproduce el audio TTS o consulta la guía en Markdown.

---

## 💻 Uso desde Terminal (CLI)

- **Grabar una clase en segundo plano:**
  ```bash
  uv run classanalizer start "Redes_de_Computadoras"
  ```
- **Ver cronómetro y estado en tiempo real:**
  ```bash
  uv run classanalizer watch
  ```
- **Detener y procesar la guía:**
  ```bash
  uv run classanalizer stop
  ```
- **Analizar un archivo existente por comando:**
  ```bash
  uv run classanalizer analyze /ruta/a/clase.mp4 --subject "Teoria_de_Sistemas"
  ```

---

## 🤖 Integración con OpenClaw
Consulta la carpeta [`openclaw_skill/`](openclaw_skill/) para usar ClassAnalizer con tu agente personal.

---

## 📄 Licencia

Este proyecto está distribuido bajo los términos de la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más información.

