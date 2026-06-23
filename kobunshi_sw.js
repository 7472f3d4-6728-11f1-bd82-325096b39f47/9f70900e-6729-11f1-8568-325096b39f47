/* 高分子化学 — PWA Service Worker */
const CACHE_NAME = 'kobunshi-pwa-v1';
const ASSETS = ['./kobunshi.html', './kobunshi_manifest.json'];
self.addEventListener('install', e => {
  e.waitUntil((async () => {
    try { const c = await caches.open(CACHE_NAME); await Promise.all(ASSETS.map(u => c.add(u).catch(()=>{}))); } catch(_) {}
    await self.skipWaiting();
  })());
});
self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    try { const ks = await caches.keys(); await Promise.all(ks.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))); } catch(_) {}
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  // GAS同期・外部は常にネットワーク（キャッシュ非対象）
  if (req.url.includes('script.google.com') || !req.url.startsWith(self.location.origin)) return;
  if (req.mode === 'navigate') {
    // ナビゲーションはネットワーク優先（更新を即反映、オフライン時はキャッシュ）
    e.respondWith((async () => {
      try { const r = await fetch(req); const c = await caches.open(CACHE_NAME); c.put(req, r.clone()); return r; }
      catch(_) { return (await caches.match(req)) || (await caches.match('./kobunshi.html')) || new Response('', {status:504}); }
    })());
    return;
  }
  e.respondWith(caches.match(req).then(r => r || fetch(req)));
});
