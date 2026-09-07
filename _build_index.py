import sys

with open('LocalTeamServer/templates/syllabary.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Point config.js to this app's own endpoint (not /readspark/config.js)
content = content.replace(
    '<script src="/readspark/config.js"></script>',
    '<script src="/config.js"></script>'
)

# 2. Remove the "← Home" back link (standalone app has no home page)
content = content.replace(
    '<a href="/" class="nav-back">\u2190 Home</a>',
    ''
)

# 3. Add PWA head tags
pwa_head = (
    '  <link rel="manifest" href="/pwa/manifest.json" />\n'
    '  <meta name="mobile-web-app-capable" content="yes" />\n'
    '  <meta name="apple-mobile-web-app-capable" content="yes" />\n'
    '  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />\n'
    '  <meta name="apple-mobile-web-app-title" content="Pagbasa" />\n'
    '  <meta name="theme-color" content="#7c3aed" />\n'
    '  <link rel="apple-touch-icon" href="/pwa/icons/icon-192.png" />'
)
content = content.replace(
    '  <script src="/config.js"></script>',
    '  <script src="/config.js"></script>\n' + pwa_head
)

# 4. Add install banner + service worker before </body>
pwa_script = (
    '\n<!-- PWA Install Banner -->\n'
    '<div id="pwa-banner" style="display:none;position:fixed;bottom:0;left:0;right:0;'
    'background:#1e1b4b;color:#fff;padding:14px 16px;align-items:center;'
    'justify-content:space-between;gap:12px;z-index:200;font-family:-apple-system,sans-serif;font-size:.88rem;">\n'
    '  <span>\U0001f4f2 I-install ang app sa iyong Android</span>\n'
    '  <div style="display:flex;gap:8px;flex-shrink:0;">\n'
    '    <button id="pwa-install-btn" style="background:#7c3aed;color:#fff;border:none;border-radius:8px;padding:8px 14px;font-weight:700;cursor:pointer;font-size:.85rem;">I-install</button>\n'
    '    <button onclick="document.getElementById(&apos;pwa-banner&apos;).style.display=&apos;none&apos;" '
    'style="background:rgba(255,255,255,.15);color:#fff;border:none;border-radius:8px;padding:8px 10px;cursor:pointer;font-size:.85rem;">\u2715</button>\n'
    '  </div>\n'
    '</div>\n\n'
    '<script>\n'
    "if ('serviceWorker' in navigator) {\n"
    "  window.addEventListener('load', () => {\n"
    "    navigator.serviceWorker.register('/pwa/sw.js', { scope: '/pwa/' })\n"
    "      .then(reg => console.log('SW registered:', reg.scope))\n"
    "      .catch(err => console.warn('SW failed:', err));\n"
    "  });\n"
    "}\n\n"
    "let deferredPrompt = null;\n"
    "window.addEventListener('beforeinstallprompt', e => {\n"
    "  e.preventDefault();\n"
    "  deferredPrompt = e;\n"
    "  const b = document.getElementById('pwa-banner');\n"
    "  if (b) b.style.display = 'flex';\n"
    "});\n\n"
    "const installBtn = document.getElementById('pwa-install-btn');\n"
    "if (installBtn) {\n"
    "  installBtn.addEventListener('click', async () => {\n"
    "    if (!deferredPrompt) return;\n"
    "    deferredPrompt.prompt();\n"
    "    const { outcome } = await deferredPrompt.userChoice;\n"
    "    deferredPrompt = null;\n"
    "    document.getElementById('pwa-banner').style.display = 'none';\n"
    "  });\n"
    "}\n\n"
    "window.addEventListener('appinstalled', () => {\n"
    "  const b = document.getElementById('pwa-banner');\n"
    "  if (b) b.style.display = 'none';\n"
    "  deferredPrompt = null;\n"
    "});\n"
    '</script>\n'
)

content = content.replace('</body>', pwa_script + '</body>')

with open('pagbasa-app/static/pwa/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done. Size:', len(content))
checks = ['\U0001f4ca', '\u270f', '\U0001f50a', '\u25fc', '\U0001f4f2', '\u2715', '\u25b6']
for c in checks:
    ok = c in content
    sys.stdout.buffer.write(f'  {repr(c)}: {ok}\n'.encode('utf-8'))
