# 🎓 ClassAnalizer

**ClassAnalizer** es un sistema inteligente para grabar clases virtuales (Google Meet, Zoom, Teams) o presenciales en Linux (PipeWire/PulseAudio), procesar el audio directamente con la API multimodal de **Google Gemini 2.0 / 1.5 Flash**, y generar automáticamente:

1. 📄 **Guía de Estudio en Markdown (`.md`)**: Estructurada pedagógicamente con resumen ejecutivo, cronología, desarrollo conceptual a fondo, glosario y banco de preguntas tipo examen.
2. 📕 **Documento PDF maquetado (`.pdf`)**: Formato limpio listo para imprimir y estudiar.
3. 🔊 **Resumen Narrado en Audio (`.mp3`)**: Síntesis de voz neuronal (TTS en español) de los conceptos fundamentales.
4. 🤖 **Skill para OpenClaw**: Control conversacional mediante comandos de chat.

---

## 🚀 Requisitos e Instalación

El proyecto está gestionado con **`uv`** para máxima velocidad y reproducibilidad.

### 1. Configurar tu API Key de Gemini
Copia el archivo de plantilla `.env.example` a `.env` y coloca tu clave:

```bash
cp .env.example .env
```

Edita `.env`:
```env
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-2.5-flash
OUTPUT_DIR=~/Clases
TTS_VOICE=es-MX-JorgeNeural
```
> *Puedes obtener una API Key gratuita en [Google AI Studio](https://aistudio.google.com/app/apikey).*

---

## 🎙️ Uso desde la Terminal (CLI)

### Iniciar grabación de una clase:
```bash
# Graba la salida de Google Meet + tu micrófono
uv run classanalizer start "Redes_de_Computadoras"

# Opciones de fuente (--source both | meet | mic):
uv run classanalizer start "Sistemas_Operativos" --source meet
```

### Consultar estado y tiempo transcurrido:
```bash
uv run classanalizer status
```

### Detener grabación y generar guías automáticamente:
```bash
uv run classanalizer stop
```
*(Detendrá `ffmpeg`, subirá el audio a Gemini, y creará el `.md`, `.pdf` y `.mp3` en `~/Clases/<Materia>/<Fecha>/`)*.

### Analizar un audio ya grabado previamente:
```bash
uv run classanalizer analyze /ruta/a/clase.mp3 --subject "Base_de_Datos"
```

---

## 🤖 Integración con Agente OpenClaw

En la carpeta [`openclaw_skill/`](openclaw_skill/) encontrarás la definición para OpenClaw:

- **`SKILL.md`**: Define los triggers e intenciones conversacionales.
- **`bridge.py`**: Interfaz ejecutable que devuelve respuestas en JSON para que el agente te informe en tiempo real y te envíe los archivos adjuntos.
