from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)

# ─────────────────────────────────────────────
#  Config básica
# ─────────────────────────────────────────────
app.config["DEBUG"] = True
app.config["SITE_NAME"] = "Mobatai"
app.config["SITE_TAGLINE"] = "Automatizaciones y webs 100% a medida."


# ─────────────────────────────────────────────
#  Context processor → variables globales en templates
# ─────────────────────────────────────────────
@app.context_processor
def inject_globals():
    return {
        "site_name": app.config["SITE_NAME"],
        "tagline": app.config["SITE_TAGLINE"],
        "year": datetime.now().year,
    }


# ─────────────────────────────────────────────
#  Rutas principales
# ─────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/propuesta")
def propuesta():
    return render_template("propuesta.html")


# ─────────────────────────────────────────────
#  API: Formulario de contacto
# ─────────────────────────────────────────────
@app.route("/api/contact", methods=["POST"])
def api_contact():
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({"ok": False, "error": "Faltan campos"}), 400

    print(f"[CONTACT] {name} <{email}> → {message}")
    return jsonify({"ok": True, "msg": "Mensaje recibido. Te contactamos pronto."})


# ─────────────────────────────────────────────
#  API: Generador de propuesta con IA
# ─────────────────────────────────────────────
@app.route("/api/generar-propuesta", methods=["POST"])
def api_generar_propuesta():
    data = request.get_json()

    negocio     = data.get("negocio", "").strip()
    problema    = data.get("problema", "").strip()
    horas       = data.get("horas", "").strip()
    herramientas = data.get("herramientas", "").strip()

    if not negocio or not problema:
        return jsonify({"ok": False, "error": "Faltan datos del negocio o el problema."}), 400

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"ok": False, "error": "API key no configurada. Contactanos directamente por WhatsApp."}), 500

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""Sos el asistente de Mobatai, un estudio de automatización y desarrollo web 100% personalizado con sede en Buenos Aires, Argentina.

Un visitante completó un formulario de diagnóstico con esta información:

- Negocio / emprendimiento: {negocio}
- Problema o tarea que le consume tiempo: {problema}
- Horas semanales estimadas perdidas: {horas if horas else "No especificado"}
- Herramientas que usa hoy: {herramientas if herramientas else "No especificado"}

Tu tarea es generar una propuesta preliminar clara, cálida y concreta. Tenés que:

1. Mostrar que entendiste el problema con una frase empática y directa (no genérica).
2. Proponer 2 o 3 ideas de solución específicas y viables (automatización, web, o ambas), explicadas en lenguaje simple, sin tecnicismos.
3. Estimar de forma realista cuánto tiempo semanal se podría recuperar (si aplica).
4. Aclarar que esto es una propuesta preliminar y que la solución real se define en una charla sin costo.
5. Terminar con un llamado a la acción cálido para que nos contacten por WhatsApp.

Tono: cercano, honesto, sin exagerar ni prometer cosas imposibles. Nada de frases corporativas. Usá tuteo argentino (vos, tenés, hacés). Formato: HTML simple con párrafos (<p>), negrita (<strong>) y listas (<ul><li>) donde ayude a la lectura. Sin CSS inline. Sin headings grandes (máximo <h4>). Máximo 350 palabras. Respondé SOLO con el HTML, sin explicaciones extra ni bloques de código."""

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        propuesta_html = response.text

        # Limpiar bloques de código si Gemini los agrega
        propuesta_html = propuesta_html.strip()
        if propuesta_html.startswith("```"):
            propuesta_html = propuesta_html.split("\n", 1)[-1]
            propuesta_html = propuesta_html.rsplit("```", 1)[0].strip()

        print(f"[PROPUESTA] Negocio: {negocio} | Problema: {problema[:60]}...")
        return jsonify({"ok": True, "propuesta": propuesta_html})

    except Exception as e:
        print(f"[ERROR GEMINI] {e}")
        return jsonify({"ok": False, "error": "Error al generar la propuesta. Intentá de nuevo o escribinos directo."}), 500


# ─────────────────────────────────────────────
#  Run
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
