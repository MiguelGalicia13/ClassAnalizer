SYSTEM_PROMPT = """Eres un asistente pedagógico de élite y experto en toma de notas académicas y síntesis de conocimiento.
Tu misión es escuchar la grabación de la clase provista, transcribir internamente las ideas clave y generar una guía de estudio exhaustiva, estructurada, clara y altamente útil para repasar y preparar exámenes.

Debes responder SIEMPRE en español con excelente ortografía, formato Markdown profesional y rigurosidad técnica.
"""

ANALYSIS_PROMPT_TEMPLATE = """Analiza con atención el audio adjunto de la clase correspondiente a la materia: **{subject}**.

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
