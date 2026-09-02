SYSTEM_PROMPT_ES = """Eres un asistente pedagógico de élite y experto en toma de notas académicas y síntesis de conocimiento.
Tu misión es escuchar la grabación de la clase provista, transcribir internamente las ideas clave y generar una guía de estudio exhaustiva, estructurada, clara y altamente útil para repasar y preparar exámenes.

Debes responder SIEMPRE en español con excelente ortografía, formato Markdown profesional y rigurosidad técnica.
"""

SYSTEM_PROMPT_EN = """You are an elite academic assistant and expert note-taker specializing in lecture synthesis.
Your mission is to listen to the provided class recording, capture key concepts, and generate a comprehensive, structured, clear, and highly practical study guide for reviewing and exam preparation.

You must ALWAYS respond in English with flawless grammar and spelling, professional Markdown formatting, and technical rigor.
"""

SYSTEM_PROMPT_AUTO = """You are an elite academic assistant and expert note-taker specializing in lecture synthesis.
Your mission is to listen to the provided class recording, capture key concepts, and generate a comprehensive, structured, clear, and highly practical study guide for reviewing and exam preparation.

IMPORTANT LANGUAGE RULE:
- Detect the primary language used in the lecture (Spanish or English).
- Generate the entire study guide, section headings, and the TTS summary in that SAME language.
- If the lecture is in Spanish, write entirely in Spanish with flawless spelling, professional Markdown, and technical rigor.
- If the lecture is in English, write entirely in English with flawless grammar, professional Markdown, and technical rigor.
"""

# Alias retrocompatible por defecto
SYSTEM_PROMPT = SYSTEM_PROMPT_AUTO

ANALYSIS_PROMPT_TEMPLATE_ES = """Analiza con atención el audio adjunto de la clase correspondiente a la materia: **{subject}**.

Genera un reporte estructurado en formato Markdown que contenga exactamente las siguientes secciones:

# 📚 Guía de Estudio: {subject}
**Fecha:** {date}  
**Tema Principal Identificado:** [Título descriptivo del tema central de la clase]  
**Oradores/Participantes:** [Docente y mención de intervenciones de estudiantes si las hay]

---

## ⚡ 1. Resumen Ejecutivo (Los 3 a 5 puntos indispensables)
* [Punto clave 1]
* [Punto clave 2]
* [Punto clave 3]
* [Punto clave 4]
* [Punto clave 5]

---

## ⏱️ 2. Cronología y Mapa de Temas
* **Inicio - [MM:SS]:** Introducción y contexto previo.
* **[MM:SS] - [MM:SS]:** [Nombre del tema o bloque].
* **[MM:SS] - Final:** Conclusiones, dudas y cierre.

---

## 📖 3. Desarrollo Conceptual a Fondo
Desarrolla en profundidad cada uno de los temas tratados en clase:
- Explicaciones detalladas con el razonamiento del profesor.
- Definiciones formales y términos técnicos.
- Fórmulas matemáticas, diagramas en texto o fragmentos de código si aplicaron.
- Ejemplos prácticos, analogías y casos de uso mencionados en clase.
- Advertencias o errores comunes señalados por el profesor ("Ojo con esto para el examen").

---

## 🗂️ 4. Glosario de Términos Clave
* **[Término 1]:** Definición clara y concisa en el contexto de la clase.
* **[Término 2]:** Definición.
* **[Término 3]:** Definición.

---

## 🎯 5. Banco de Preguntas para Examen (Autoevaluación)
Crea 5 a 8 preguntas tipo examen con sus respectivas respuestas desplegables o explicadas:
1. **Pregunta:** [Pregunta conceptual o práctica]
   - **Respuesta esperada:** [Explicación de la respuesta correcta]
2. **Pregunta:** [...]
   - **Respuesta esperada:** [...]

---

## 📌 6. Tareas, Avisos y Próximos Pasos
* [Mención de lecturas obligatorias, entregas de proyectos, tareas o fechas de parciales anunciadas durante la sesión. Si no se mencionaron, indícalo expresamente.]

---

## 🎙️ RESUMEN_TTS_INICIO
[Escribe aquí un resumen narrativo de 150 a 250 palabras, con tono fluido, natural y directo en primera persona o tono de narrador para ser leído por un motor de voz TTS. Debe resumir lo esencial de la clase sin listas con viñetas ni símbolos raros].
## 🎙️ RESUMEN_TTS_FIN
"""

ANALYSIS_PROMPT_TEMPLATE_EN = """Carefully analyze the attached class audio for the subject: **{subject}**.

Generate a structured study guide in Markdown format containing exactly the following sections:

# 📚 Study Guide: {subject}
**Date:** {date}  
**Main Identified Topic:** [Descriptive title of the core topic of the lecture]  
**Speakers/Participants:** [Instructor and notable student contributions if any]

---

## ⚡ 1. Executive Summary (The 3 to 5 indispensable takeaways)
* [Key point 1]
* [Key point 2]
* [Key point 3]
* [Key point 4]
* [Key point 5]

---

## ⏱️ 2. Timeline and Topic Map
* **Start - [MM:SS]:** Introduction and prior context.
* **[MM:SS] - [MM:SS]:** [Topic or module name].
* **[MM:SS] - End:** Conclusions, questions, and wrap-up.

---

## 📖 3. In-Depth Conceptual Development
Thoroughly develop each topic covered in class:
- Detailed explanations capturing the instructor's reasoning.
- Formal definitions and technical terminology.
- Mathematical formulas, text diagrams, or code snippets if applicable.
- Practical examples, analogies, and use cases discussed in lecture.
- Warnings or common mistakes emphasized by the instructor ("Pay attention to this for the exam").

---

## 🗂️ 4. Key Terms Glossary
* **[Term 1]:** Clear and concise definition in the context of the lecture.
* **[Term 2]:** Definition.
* **[Term 3]:** Definition.

---

## 🎯 5. Exam Question Bank (Self-Assessment)
Create 5 to 8 exam-style questions with comprehensive answers:
1. **Question:** [Conceptual or practical question]
   - **Expected Answer:** [Clear explanation of the correct solution]
2. **Question:** [...]
   - **Expected Answer:** [...]

---

## 📌 6. Assignments, Announcements & Next Steps
* [Mention required readings, project deadlines, homework, or exam dates announced during the session. If none were mentioned, explicitly state so.]

---

## 🎙️ RESUMEN_TTS_INICIO
[Write a narrative summary here of 150 to 250 words, with a smooth, natural, and direct narrator tone to be spoken by a TTS engine. It must summarize the lecture essentials without bullet lists or special symbols].
## 🎙️ RESUMEN_TTS_FIN
"""

ANALYSIS_PROMPT_TEMPLATE_AUTO = """Analyze the attached class audio for the subject: **{subject}**.

Detect the language used in the lecture (Spanish or English) and generate a structured study guide in Markdown in that SAME language adhering to the following structure:

[IF SPANISH LECTURE]
# 📚 Guía de Estudio: {subject}
**Fecha:** {date}  
**Tema Principal Identificado:** [Título descriptivo]  
**Oradores/Participantes:** [Docente e intervenciones]

---
## ⚡ 1. Resumen Ejecutivo (Los 3 a 5 puntos indispensables)
## ⏱️ 2. Cronología y Mapa de Temas
## 📖 3. Desarrollo Conceptual a Fondo
## 🗂️ 4. Glosario de Términos Clave
## 🎯 5. Banco de Preguntas para Examen (Autoevaluación)
## 📌 6. Tareas, Avisos y Próximos Pasos
## 🎙️ RESUMEN_TTS_INICIO
[Resumen narrativo de 150 a 250 palabras para TTS]
## 🎙️ RESUMEN_TTS_FIN

[IF ENGLISH LECTURE]
# 📚 Study Guide: {subject}
**Date:** {date}  
**Main Identified Topic:** [Descriptive title]  
**Speakers/Participants:** [Instructor and participants]

---
## ⚡ 1. Executive Summary (The 3 to 5 indispensable takeaways)
## ⏱️ 2. Timeline and Topic Map
## 📖 3. In-Depth Conceptual Development
## 🗂️ 4. Key Terms Glossary
## 🎯 5. Exam Question Bank (Self-Assessment)
## 📌 6. Assignments, Announcements & Next Steps
## 🎙️ RESUMEN_TTS_INICIO
[Narrative summary of 150 to 250 words for TTS]
## 🎙️ RESUMEN_TTS_FIN
"""

# Alias retrocompatible por defecto
ANALYSIS_PROMPT_TEMPLATE = ANALYSIS_PROMPT_TEMPLATE_AUTO


def get_prompts(
    subject: str,
    date_str: str,
    language: str = "auto",
) -> tuple[str, str]:
    """
    Devuelve la tupla (system_prompt, user_prompt) adaptada al idioma seleccionado.
    language: 'auto', 'es', 'en'
    """
    lang = (language or "auto").strip().lower()
    if lang.startswith("es"):
        sys_p = SYSTEM_PROMPT_ES
        tmpl = ANALYSIS_PROMPT_TEMPLATE_ES
    elif lang.startswith("en"):
        sys_p = SYSTEM_PROMPT_EN
        tmpl = ANALYSIS_PROMPT_TEMPLATE_EN
    else:
        sys_p = SYSTEM_PROMPT_AUTO
        tmpl = ANALYSIS_PROMPT_TEMPLATE_AUTO

    user_p = tmpl.format(subject=subject, date=date_str)
    return sys_p, user_p

