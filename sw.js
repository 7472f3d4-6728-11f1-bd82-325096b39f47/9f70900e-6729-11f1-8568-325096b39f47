const CACHE_NAME = 'muki-mikan-v2';
const ASSETS = [
  './muki_mikan.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      // addAll fails if any asset fails; use individual add with catch instead
      return Promise.all(
        ASSETS.map(url => cache.add(url).catch(err => console.warn('[SW] cache miss:', url, err)))
      );
    }).then(() => {
      console.log('[SW] installed, cache:', CACHE_NAME);
      return self.skipWaiting();
    })
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => {
          console.log('[SW] deleting old cache:', k);
          return caches.delete(k);
        })
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const url = e.request.url;
  // GAS sync and external requests: always network
  if (url.includes('script.google.com') || !url.startsWith(self.location.origin)) return;

  e.respondWith(
    caches.match(e.request).then(cached => {
      if (cached) return cached;
      return fetch(e.request).then(res => {
        // Cache successful same-origin GET responses
        if (res && res.status === 200 && e.request.method === 'GET') {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        }
        return res;
      });
    }).catch(() => caches.match('./muki_mikan.html'))
  );
});
