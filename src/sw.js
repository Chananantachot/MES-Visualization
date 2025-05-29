const CACHE_NAME = 'flask-site-cache-v1';
const OFFLINE_URL = '/static/offline.html';
console.log('🔥 Service worker file loaded');
const assetsToCache = [
    '/',
    '/api/machines/download_csv',
    '/api/machines/health',
    '/productionRates',
    '/productionRates/data',
    '/productionRates/chart/data',
    '/productionRates/download_csv',
    '/motor',
    '/motor/data',
    '/motor/chart/data',
    '/motor/download_csv',
    '/senser',
    '/senser/data',
    '/senser/chart/data',
    '/senser/download_csv',
    '/iotDevices',
    '/static/app.css',
    '/static/app.js',
    '/static/data/MOCK_DATA.json',
    '/static/manifest.json',
    '/static/logo.png',
    '/static/new_account.png'
];

const retryCaches = []

self.addEventListener('install', event => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open('my-cache-v1');
      for (const url of assetsToCache) {
        try {
          const response = await fetch(url);
          if (response.ok) {
            await cache.put(url, response.clone());
          }
        } catch (err) {
           retryCaches.push(url);
          console.warn(`Failed to cache ${url}`, err);
        }
      }
    })()
  );
  self.skipWaiting();
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Check if request URL path is in the cached assets list
  console.log(url.pathname);
  if (assetsToCache.includes(url.pathname)) {
    event.respondWith(
      caches.open(CACHE_NAME).then(async cache => {
        const cachedResponse = await cache.match(event.request);
        if (cachedResponse) {
          return cachedResponse;
        }

        // If not cached, fetch from network and cache it
        const networkResponse = await fetch(event.request);
        if (networkResponse && networkResponse.ok) {
          cache.put(event.request, networkResponse.clone());
        }
        return networkResponse;
      })
    );
  }
  // else: allow normal fetch for non-cached assets
});


self.addEventListener('activate', event => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('sync', event => {
    if (event.tag === 'retry-request') {
        event.waitUntil(retryCacheLogic());
    }
});

async function retryCacheLogic() {
  const cache = await caches.open('my-cache-v1');
  if (retryCaches.length > 0)
  {
    for (const url of retryCaches) {
        try {
            const response = await fetch(url);
            if (response.ok) {
                await cache.put(url, response.clone());
                console.log('✅ Retried and cached:', url);
            }
        } catch (err) {
            console.warn('❌ Still failed:', url, err);
        }
    }
  }
}