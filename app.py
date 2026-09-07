import os
from flask import Flask, send_from_directory, jsonify

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# ── TTS credentials from environment ─────────────────────────────────────────
ELEVENLABS_API_KEY     = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID_EN = os.environ.get("ELEVENLABS_VOICE_ID_EN", "JBFqnCBsd6RMkjVDRZzb")
ELEVENLABS_VOICE_ID_TL = os.environ.get("ELEVENLABS_VOICE_ID_TL", "JBFqnCBsd6RMkjVDRZzb")
ELEVENLABS_MODEL       = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")

WATSON_TTS_API_KEY  = os.environ.get("WATSON_TTS_API_KEY", "")
WATSON_TTS_URL      = os.environ.get("WATSON_TTS_URL", "")
WATSON_TTS_VOICE    = os.environ.get("WATSON_TTS_VOICE", "en-US_EmilyV3Voice")
WATSON_TTS_VOICE_TL = os.environ.get("WATSON_TTS_VOICE_TL", "en-US_EmilyV3Voice")
WATSON_TTS_FORMAT   = os.environ.get("WATSON_TTS_FORMAT", "audio/mp3")

# ── Static directories ────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(__file__)
PWA_DIR   = os.path.join(BASE_DIR, "static", "pwa")
ICONS_DIR = os.path.join(PWA_DIR, "icons")

# ── Config endpoint — serves TTS credentials as JS (never in static files) ───
@app.route("/config.js")
@app.route("/pwa/config.js")
def config_js():
    js = (
        "const ELEVENLABS_CONFIG = {{\n"
        '  apiKey:    "{el_key}",\n'
        '  voiceIdEN: "{el_voice_en}",\n'
        '  voiceIdTL: "{el_voice_tl}",\n'
        '  model:     "{el_model}",\n'
        "}};\n\n"
        "const WATSON_CONFIG = {{\n"
        '  apiKey:  "{watson_key}",\n'
        '  url:     "{watson_url}",\n'
        '  voice:   "{watson_voice}",\n'
        '  voiceTL: "{watson_voice_tl}",\n'
        '  format:  "{watson_fmt}",\n'
        "}};\n"
    ).format(
        el_key=ELEVENLABS_API_KEY,
        el_voice_en=ELEVENLABS_VOICE_ID_EN,
        el_voice_tl=ELEVENLABS_VOICE_ID_TL,
        el_model=ELEVENLABS_MODEL,
        watson_key=WATSON_TTS_API_KEY,
        watson_url=WATSON_TTS_URL,
        watson_voice=WATSON_TTS_VOICE,
        watson_voice_tl=WATSON_TTS_VOICE_TL,
        watson_fmt=WATSON_TTS_FORMAT,
    )
    return js, 200, {"Content-Type": "application/javascript; charset=utf-8"}

# ── Health check ──────────────────────────────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "Unang Hakbang sa Pagbasa"})

# ── PWA routes ────────────────────────────────────────────────────────────────
@app.route("/")
@app.route("/pwa/")
@app.route("/pwa/index.html")
def index():
    return send_from_directory(PWA_DIR, "index.html",
                               mimetype="text/html; charset=utf-8")

@app.route("/pwa/manifest.json")
def manifest():
    return send_from_directory(PWA_DIR, "manifest.json",
                               mimetype="application/manifest+json")

@app.route("/pwa/sw.js")
def sw():
    return send_from_directory(PWA_DIR, "sw.js",
                               mimetype="application/javascript")

@app.route("/pwa/icons/<path:filename>")
def icons(filename):
    return send_from_directory(ICONS_DIR, filename)

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
