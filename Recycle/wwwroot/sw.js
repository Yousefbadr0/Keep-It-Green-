/* Keep It Green — service worker (network-first, API bypassed) */
const CACHE = 'kig-v4';
const SHELL = ['/', '/index.html', '/css/style.css', '/css/fonts.css', '/css/kiosk-fonts.css', '/js/api.js', '/js/app.js', '/manifest.webmanifest'];

self.addEventListener('install', (e) => {
    self.skipWaiting();
    e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL).catch(() => {})));
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys()
            .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (e) => {
    const url = new URL(e.request.url);
    // Never cache API calls — always hit the network.
    if (e.request.method !== 'GET' || url.pathname.startsWith('/api/')) return;
    e.respondWith(
        fetch(e.request)
            .then((res) => {
                const copy = res.clone();
                caches.open(CACHE).then((c) => c.put(e.request, copy)).catch(() => {});
                return res;
            })
            .catch(() => caches.match(e.request).then((r) => r || caches.match('/')))
    );
});
