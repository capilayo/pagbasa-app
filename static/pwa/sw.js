const CACHE_NAME = 'pagbasa-v1';
const ASSETS = [
  '/pwa/',
  '/pwa/index.html',
  '/pwa/manifest.json',
  '/pwa/icons/icon-192.png',
  '/pwa/icons/icon-512.png',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  // Always network-first for TTS API calls and config
  if (
    url.hostname.includes('elevenlabs.io') ||
    url.hostname.includes('watson.cloud.ibm.com') ||
    url.pathname === '/config.js' ||
    url.pathname === '/pwa/config.js'
  ) {
    event.respondWith(fetch(event.request));
    return;
  }
  // Cache-first for app shell
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});
