# Unang Hakbang sa Pagbasa — IBM Code Engine Deployment

A standalone PWA (Progressive Web App) for Filipino syllabary reading practice,
powered by ElevenLabs TTS (Tagalog) with IBM Watson TTS as fallback.

---

## Folder structure

```
pagbasa-app/
├── app.py                  ← Flask app (serves config.js + PWA static files)
├── Dockerfile              ← Red Hat UBI9 Python 3.11 image
├── requirements.txt        ← Flask, gunicorn, python-dotenv
├── env.sample              ← credential template (copy → .env for local dev)
└── static/pwa/
    ├── index.html          ← PWA app shell (syllabary + custom lesson)
    ├── manifest.json       ← PWA manifest (name, icons, theme)
    ├── sw.js               ← Service worker (offline cache)
    └── icons/
        ├── icon-192.png
        └── icon-512.png
```

---

## Local development

```powershell
cd pagbasa-app

# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env from sample and fill in credentials
copy env.sample .env

# 3. Run
python app.py
# → http://localhost:8080/pwa/
```

---

## Deploy to IBM Code Engine

### Prerequisites (once only)

```bash
# Install IBM Cloud CLI + Code Engine plugin
ibmcloud plugin install code-engine

# Log in
ibmcloud login --sso

# Select resource group and region
ibmcloud target -g default -r jp-tok   # change region as needed

# Select (or create) a Code Engine project
ibmcloud ce project select --name my-apps
# ibmcloud ce project create --name my-apps  # if it doesn't exist yet
```

---

### Step 1 — Store credentials as a Code Engine secret

**Never pass API keys as plain `--env` flags.** Use a secret:

```bash
ibmcloud ce secret create --name pagbasa-tts-creds \
  --from-literal ELEVENLABS_API_KEY=your_elevenlabs_key \
  --from-literal ELEVENLABS_VOICE_ID_EN=JBFqnCBsd6RMkjVDRZzb \
  --from-literal ELEVENLABS_VOICE_ID_TL=JBFqnCBsd6RMkjVDRZzb \
  --from-literal ELEVENLABS_MODEL=eleven_multilingual_v2 \
  --from-literal WATSON_TTS_API_KEY=your_watson_key \
  --from-literal WATSON_TTS_URL=https://api.jp-tok.text-to-speech.watson.cloud.ibm.com/instances/YOUR_ID \
  --from-literal WATSON_TTS_VOICE=en-US_EmilyV3Voice \
  --from-literal WATSON_TTS_VOICE_TL=en-US_EmilyV3Voice \
  --from-literal WATSON_TTS_FORMAT=audio/mp3
```

---

### Step 2 — Deploy the app

Run this from the `pagbasa-app/` directory:

```bash
cd pagbasa-app

ibmcloud ce app create \
  --name pagbasa-app \
  --build-source . \
  --strategy dockerfile \
  --port 8080 \
  --min-scale 0 \
  --max-scale 3 \
  --cpu 0.25 \
  --memory 0.5G \
  --env-from-secret pagbasa-tts-creds
```

Code Engine will:
1. Build the Docker image from your `Dockerfile`
2. Push it to an internal registry
3. Deploy and give you a public HTTPS URL

---

### Step 3 — Get the public URL

```bash
ibmcloud ce app get --name pagbasa-app --output url
```

Output will look like:
```
https://pagbasa-app.XXXXXXXXXX.jp-tok.codeengine.appdomain.cloud
```

Share this URL with students — they can open it in Chrome on Android and
tap **"Add to Home Screen"** / **"I-install"** to install it as an app.

---

### Step 4 — Verify

```bash
# Health check
curl https://pagbasa-app.XXXXXXXXXX.jp-tok.codeengine.appdomain.cloud/health
# Expected: {"app":"Unang Hakbang sa Pagbasa","status":"ok"}

# Config endpoint (should return JS with credential vars, no actual key values shown here)
curl https://pagbasa-app.XXXXXXXXXX.jp-tok.codeengine.appdomain.cloud/config.js
```

---

## Update the deployment

After any code change:

```bash
cd pagbasa-app

# Rebuild index.html if syllabary template changed
python _build_index.py

# Redeploy
ibmcloud ce app update \
  --name pagbasa-app \
  --build-source .
```

---

## Update credentials

```bash
ibmcloud ce secret update --name pagbasa-tts-creds \
  --from-literal ELEVENLABS_API_KEY=new_key_here

# Restart the app to pick up the new secret
ibmcloud ce app restart --name pagbasa-app
```

---

## Scale / teardown

```bash
# Scale to always-on (no cold start)
ibmcloud ce app update --name pagbasa-app --min-scale 1

# Delete entirely
ibmcloud ce app delete --name pagbasa-app --force
ibmcloud ce secret delete --name pagbasa-tts-creds --force
```

---

## Architecture

```
Android Chrome
    │  (HTTPS)
    ▼
IBM Code Engine: pagbasa-app
    ├── GET /          → static/pwa/index.html  (app shell)
    ├── GET /config.js → Flask injects env vars as JS constants
    ├── GET /pwa/sw.js → service worker
    └── GET /health    → {"status":"ok"}
    │
    ▼ (from browser, not from server)
ElevenLabs API  →  audio/mp3  (primary TTS — real Tagalog)
IBM Watson TTS  →  audio/mp3  (fallback)
```

---

*Generated with IBM Bob*
