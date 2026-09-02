import argparse
import sys
import time
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live

from classanalizer.recorder import AudioRecorder
from classanalizer.analyzer_factory import (
    create_analyzer,
    list_models_for_provider,
    normalize_provider,
    validate_provider_key,
)
from classanalizer.exporter import Exporter
from classanalizer.config import (
    AI_PROVIDER,
    ANTHROPIC_MODEL,
    GEMINI_MODEL,
    OUTPUT_DIR,
    TTS_VOICE,
)
from classanalizer.platform import send_desktop_notification

console = Console()

def send_notification(title: str, message: str, urgency: str = "normal"):
    """Envía una notificación usando el backend del sistema operativo."""
    send_desktop_notification(title, message, urgency)

def format_seconds(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def get_file_size_str(filepath: Path) -> str:
    if not filepath.exists():
        return "0 KB"
    size_bytes = filepath.stat().st_size
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"

def cmd_gui(args=None):
    from classanalizer.gui.app import launch_gui
    launch_gui()

def cmd_start(args):
    try:
        session = AudioRecorder.start_recording(subject=args.subject, source=args.source)
        send_notification(
            "🔴 Grabación Iniciada",
            f"Materia: {session['subject']}\nFuente: {session['source']}"
        )
        console.print(Panel.fit(
            f"[bold green]▶ Grabación iniciada con éxito[/bold green]\n\n"
            f"[cyan]Materia:[/cyan] {session['subject']}\n"
            f"[cyan]Fuente:[/cyan] {session['source']} (Meet + Mic)\n"
            f"[cyan]Destino de audio:[/cyan] {session['audio_file']}\n"
            f"[cyan]PID:[/cyan] {session['pid']}\n\n"
            f"[dim]Usa 'classanalizer watch' para monitoreo en vivo o 'classanalizer stop' para terminar.[/dim]",
            title="🎙️ ClassAnalizer"
        ))
    except Exception as e:
        console.print(f"[bold red]Error iniciando grabación:[/bold red] {e}")
        sys.exit(1)

def cmd_status(args):
    session = AudioRecorder.get_session_info()
    if not session:
        console.print("[yellow]ℹ No hay ninguna grabación activa en este momento.[/yellow]")
        return

    audio_path = Path(session.get("audio_file", ""))
    size_str = get_file_size_str(audio_path)
    elapsed_str = format_seconds(session.get("elapsed_seconds", 0))

    table = Table(title="🎙️ Estado de la Grabación Actual")
    table.add_column("Propiedad", style="cyan")
    table.add_column("Valor", style="white")

    table.add_row("Estado", "[bold green]GRABANDO 🔴[/bold green]")
    table.add_row("Materia", session.get("subject", "N/A"))
    table.add_row("Tiempo transcurrido", f"[bold yellow]{elapsed_str}[/bold yellow]")
    table.add_row("Tamaño actual", f"[bold green]{size_str}[/bold green]")
    table.add_row("Fuente", session.get("source", "both"))
    table.add_row("Archivo", str(audio_path))

    console.print(table)

def cmd_watch(args):
    """Muestra un panel interactivo en vivo con el estado, tiempo y tamaño de archivo."""
    console.clear()
    with Live(auto_refresh=False, console=console) as live:
        try:
            while True:
                session = AudioRecorder.get_session_info()
                if not session:
                    panel = Panel(
                        "[yellow]⏸ En espera: No hay ninguna grabación activa actualmente.[/yellow]\n\n"
                        "[dim]Inicia una grabación con 'classanalizer start [Materia]' o desde la interfaz gráfica.[/dim]\n"
                        "[dim]Presiona Ctrl+C para salir del monitor.[/dim]",
                        title="🎙️ ClassAnalizer Daemon Watcher"
                    )
                else:
                    audio_path = Path(session.get("audio_file", ""))
                    size_str = get_file_size_str(audio_path)
                    elapsed_str = format_seconds(session.get("elapsed_seconds", 0))

                    table = Table(title="🔴 Grabación en Curso")
                    table.add_column("Campo", style="cyan")
                    table.add_column("Detalle", style="bold white")
                    table.add_row("Materia", session.get("subject", "N/A"))
                    table.add_row("Tiempo Grabado", f"[bold yellow]{elapsed_str}[/bold yellow]")
                    table.add_row("Tamaño en Disco", f"[bold green]{size_str}[/bold green]")
                    table.add_row("Fuente de Audio", session.get("source", "both"))
                    table.add_row("PID Proceso", str(session.get("pid", "N/A")))
                    table.add_row("Ruta Archivo", str(audio_path))

                    panel = Panel(
                        table,
                        title="🎙️ ClassAnalizer Monitor en Vivo (Ctrl+C para salir)",
                        border_style="green"
                    )
                
                live.update(panel, refresh=True)
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[dim]Monitor cerrado.[/dim]")

def process_audio_file(
    audio_path: Path,
    subject: str,
    output_dir: Path,
    date_str: str = "",
    model: Optional[str] = None,
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
):
    selected_provider = normalize_provider(provider)
    if selected_provider == "anthropic":
        chosen_model = model or ANTHROPIC_MODEL or "claude-sonnet-5"
        provider_label = f"Anthropic Claude ({chosen_model})"
        processing_message = "Transcribiendo con Whisper y estructurando guía con Claude..."
    else:
        chosen_model = model or GEMINI_MODEL or "gemini-3.7-flash"
        provider_label = f"Google Gemini ({chosen_model})"
        processing_message = "Subiendo y estructurando guía pedagógica con Gemini..."

    console.print(
        f"\n[bold blue]🧠 Procesando audio con {provider_label} - "
        f"Materia: {subject}...[/bold blue]"
    )
    send_notification("🧠 Procesando Clase", f"Analizando con {provider_label}: {subject}...")

    with console.status(f"[bold green]{processing_message}") as status:
        analyzer = create_analyzer(
            provider=selected_provider,
            api_key=api_key,
            model=chosen_model,
        )
        markdown_text, tts_text = analyzer.analyze_audio(audio_path, subject=subject, date_str=date_str, model=chosen_model)
        
        status.update("[bold cyan]Exportando guía en Markdown y PDF...")
        md_file = output_dir / "guia_estudio.md"
        pdf_file = output_dir / "guia_estudio.pdf"
        tts_file = output_dir / "resumen_audio.mp3"

        Exporter.export_markdown(markdown_text, md_file)
        Exporter.export_pdf(markdown_text, pdf_file)
        
        status.update(f"[bold magenta]Generando narración en audio (TTS: {TTS_VOICE})...")
        Exporter.export_tts_audio(tts_text, tts_file, voice=TTS_VOICE)

    send_notification("✨ Guía Generada", f"Tu guía de {subject} está lista en PDF, MD y Audio.")
    console.print(Panel.fit(
        f"[bold green]✨ ¡Guía de estudio generada exitosamente![/bold green]\n\n"
        f"📄 [cyan]Markdown:[/cyan] {md_file}\n"
        f"📕 [cyan]PDF:[/cyan]      {pdf_file}\n"
        f"🔊 [cyan]Audio TTS:[/cyan] {tts_file}\n"
        f"🎙️ [cyan]Audio Raw:[/cyan] {audio_path}",
        title="🎓 Entregables Generados"
    ))

def cmd_stop(args):
    try:
        session = AudioRecorder.stop_recording()
        duration_str = format_seconds(session.get("duration_seconds", 0))
        console.print(f"[bold green]⏹ Grabación detenida.[/bold green] Duración total: [bold yellow]{duration_str}[/bold yellow]")
        
        if not args.no_analyze:
            audio_path = Path(session["audio_file"])
            output_dir = Path(session["output_dir"])
            subject = session["subject"]
            date_str = session.get("date", "")
            process_audio_file(
                audio_path,
                subject,
                output_dir,
                date_str,
                model=args.model,
                provider=args.provider,
            )
    except Exception as e:
        console.print(f"[bold red]Error deteniendo grabación:[/bold red] {e}")
        sys.exit(1)

def cmd_analyze(args):
    audio_path = Path(args.file).resolve()
    if not audio_path.exists():
        console.print(f"[bold red]Error:[/bold red] El archivo {audio_path} no existe.")
        sys.exit(1)

    subject = args.subject or audio_path.stem
    output_dir = args.outdir or audio_path.parent
    output_dir = Path(output_dir).resolve()

    try:
        process_audio_file(
            audio_path,
            subject,
            output_dir,
            model=args.model,
            provider=args.provider,
        )
    except Exception as e:
        console.print(f"[bold red]Error durante el análisis:[/bold red] {e}")
        sys.exit(1)


def cmd_validate(args):
    """Valida la API key y muestra los modelos del proveedor seleccionado."""
    provider = normalize_provider(args.provider)
    console.print(f"[bold blue]🔑 Validando API key de {provider}...[/bold blue]")
    is_valid, message = validate_provider_key(provider)
    if not is_valid:
        console.print(f"[bold red]❌ {message}[/bold red]")
        sys.exit(1)

    console.print(f"[bold green]✅ {message}[/bold green]")
    try:
        models = list_models_for_provider(provider)
        table = Table(title=f"Modelos disponibles ({provider})")
        table.add_column("ID", style="cyan")
        table.add_column("Nombre", style="white")
        for model_info in models:
            table.add_row(str(model_info["id"]), str(model_info["name"]))
        console.print(table)
    except Exception as exc:
        console.print(f"[yellow]⚠ No se pudieron listar modelos: {exc}[/yellow]")

def main():
    parser = argparse.ArgumentParser(
        prog="classanalizer",
        description="Grabador inteligente de clases y generador de guías de estudio con IA"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # GUI Desktop App
    subparsers.add_parser("gui", help="Lanza la aplicación de escritorio gráfica")

    # Start
    p_start = subparsers.add_parser("start", help="Inicia la grabación de una clase")
    p_start.add_argument("subject", nargs="?", default="Clase", help="Nombre de la materia o tema")
    p_start.add_argument(
        "--source",
        choices=["both", "meet", "mic"],
        default="both",
        help="Fuente de audio: meet (solo Google Meet), mic (solo micrófono), both (ambos)"
    )

    # Status
    subparsers.add_parser("status", help="Consulta el estado de la grabación actual")

    # Watch (Daemon Monitor)
    subparsers.add_parser("watch", help="Monitor interactivo en tiempo real del estado de grabación")

    # Stop
    p_stop = subparsers.add_parser("stop", help="Detiene la grabación y genera la guía")
    p_stop.add_argument("--no-analyze", action="store_true", help="Detiene la grabación sin procesar con IA")
    p_stop.add_argument("--provider", "-p", choices=["gemini", "anthropic"], help="Proveedor de IA")
    p_stop.add_argument("--model", "-m", default=None, help="Modelo específico del proveedor")

    # Analyze
    p_analyze = subparsers.add_parser("analyze", help="Analiza un archivo de audio ya existente")
    p_analyze.add_argument("file", help="Ruta al archivo de audio/video (.mp3, .wav, .m4a, .mp4, .mkv)")
    p_analyze.add_argument("--subject", "-s", help="Nombre de la materia")
    p_analyze.add_argument("--outdir", "-o", help="Directorio donde guardar los resultados")
    p_analyze.add_argument("--provider", "-p", choices=["gemini", "anthropic"], help="Proveedor de IA")
    p_analyze.add_argument("--model", "-m", default=None, help="Modelo específico del proveedor")

    # Validate
    p_validate = subparsers.add_parser(
        "validate",
        help="Valida la API key y lista los modelos disponibles",
    )
    p_validate.add_argument(
        "--provider",
        "-p",
        choices=["gemini", "anthropic"],
        help="Proveedor de IA (por defecto, AI_PROVIDER)",
    )

    args = parser.parse_args()

    if args.command == "gui":
        cmd_gui(args)
    elif args.command == "start":
        cmd_start(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "watch":
        cmd_watch(args)
    elif args.command == "stop":
        cmd_stop(args)
    elif args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "validate":
        cmd_validate(args)
    else:
        cmd_gui()

if __name__ == "__main__":
    main()
