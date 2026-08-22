import asyncio
from pathlib import Path
import markdown
import weasyprint
import edge_tts

from classanalizer.config import TTS_VOICE

ACADEMIC_CSS = """
@page {
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-center {
        content: "Página " counter(page) " de " counter(pages);
        font-size: 9pt;
        color: #718096;
        font-family: system-ui, -apple-system, sans-serif;
    }
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #2d3748;
    font-size: 11pt;
}

h1 {
    color: #1a365d;
    font-size: 20pt;
    border-bottom: 2px solid #3182ce;
    padding-bottom: 6px;
    margin-top: 0;
    margin-bottom: 12px;
}

h2 {
    color: #2b6cb0;
    font-size: 14pt;
    margin-top: 20px;
    margin-bottom: 8px;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 4px;
}

h3 {
    color: #2d3748;
    font-size: 12pt;
    margin-top: 14px;
    margin-bottom: 6px;
}

ul, ol {
    margin-top: 4px;
    margin-bottom: 12px;
    padding-left: 24px;
}

li {
    margin-bottom: 4px;
}

strong {
    color: #1a202c;
}

code {
    background-color: #edf2f7;
    padding: 2px 5px;
    border-radius: 4px;
    font-family: "Courier New", Courier, monospace;
    font-size: 9.5pt;
}

pre {
    background-color: #2d3748;
    color: #f7fafc;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 9.5pt;
}

pre code {
    background-color: transparent;
    color: inherit;
    padding: 0;
}

blockquote {
    border-left: 4px solid #3182ce;
    margin: 12px 0;
    padding: 8px 16px;
    background-color: #ebf8ff;
    color: #2c5282;
    border-radius: 0 6px 6px 0;
}

hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 18px 0;
}
"""

class Exporter:
    @staticmethod
    def export_markdown(markdown_content: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown_content, encoding="utf-8")
        return output_path

    @staticmethod
    def export_pdf(markdown_content: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convertir Markdown a HTML con extensiones de tablas y bloques de código
        html_body = markdown.markdown(
            markdown_content,
            extensions=["extra", "codehilite", "nl2br", "sane_lists", "toc"]
        )
        
        full_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Guía de Estudio</title>
    <style>{ACADEMIC_CSS}</style>
</head>
<body>
{html_body}
</body>
</html>"""
        
        weasyprint.HTML(string=full_html).write_pdf(target=str(output_path))
        return output_path

    @staticmethod
    def export_tts_audio(text: str, output_path: Path, voice: str = TTS_VOICE) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        async def _synthesize():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_path))

        asyncio.run(_synthesize())
        return output_path
