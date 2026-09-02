#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Añadir src al path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from classanalizer.recorder import AudioRecorder
from classanalizer.analyzer_factory import create_analyzer, normalize_provider
from classanalizer.exporter import Exporter
from classanalizer.config import TTS_VOICE

def handle_start(subject: str, source: str):
    try:
        session = AudioRecorder.start_recording(subject=subject, source=source)
        return {
            "status": "success",
            "message": f"Grabación de '{subject}' iniciada correctamente.",
            "data": session
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

def handle_status():
    session = AudioRecorder.get_session_info()
    if not session:
        return {
            "status": "idle",
            "is_recording": False,
            "message": "No hay grabaciones activas."
        }
    return {
        "status": "recording",
        "is_recording": True,
        "subject": session.get("subject"),
        "elapsed_seconds": session.get("elapsed_seconds"),
        "audio_file": session.get("audio_file")
    }

def handle_stop(
    analyze: bool = True,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    language: Optional[str] = "auto",
):
    try:
        session = AudioRecorder.stop_recording()
        result = {
            "status": "success",
            "message": f"Grabación de '{session.get('subject')}' detenida. Duración: {session.get('duration_seconds')}s.",
            "audio_file": session.get("audio_file"),
            "artifacts": {}
        }
        
        if analyze:
            audio_path = Path(session["audio_file"])
            output_dir = Path(session["output_dir"])
            subject = session["subject"]
            date_str = session.get("date", "")
            
            selected_provider = normalize_provider(provider)
            analyzer = create_analyzer(
                provider=selected_provider,
                model=model,
            )
            markdown_text, tts_text = analyzer.analyze_audio(
                audio_path,
                subject=subject,
                date_str=date_str,
                model=model,
                language=language,
            )
            
            md_file = output_dir / "guia_estudio.md"
            pdf_file = output_dir / "guia_estudio.pdf"
            tts_file = output_dir / "resumen_audio.mp3"

            Exporter.export_markdown(markdown_text, md_file)
            Exporter.export_pdf(markdown_text, pdf_file, language=language)
            Exporter.export_tts_audio(tts_text, tts_file, language=language)

            result["artifacts"] = {
                "markdown": str(md_file),
                "pdf": str(pdf_file),
                "tts_audio": str(tts_file),
                "tts_summary_text": tts_text
            }
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["start", "status", "stop"], required=True)
    parser.add_argument("--subject", default="Clase")
    parser.add_argument("--source", default="both", choices=["both", "meet", "mic"])
    parser.add_argument("--provider", choices=["gemini", "anthropic"], help="Proveedor de IA")
    parser.add_argument("--model", help="Modelo específico del proveedor")
    parser.add_argument("--language", choices=["auto", "es", "en"], default="auto", help="Idioma de salida")
    parser.add_argument("--no-analyze", action="store_true")
    parser.add_argument("--json", action="store_true", help="Salida en JSON")

    args = parser.parse_args()

    if args.action == "start":
        res = handle_start(args.subject, args.source)
    elif args.action == "status":
        res = handle_status()
    elif args.action == "stop":
        res = handle_stop(
            analyze=not args.no_analyze,
            provider=args.provider,
            model=args.model,
            language=args.language,
        )
    else:
        res = {"status": "error", "message": "Acción no reconocida"}

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(res.get("message", json.dumps(res, ensure_ascii=False)))

if __name__ == "__main__":
    main()
