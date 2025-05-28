const CACHE_NAME = 'flask-site-cache-v1';
const OFFLINE_URL = '/static/offline.html';
console.log('🔥 Service worker file loaded');
self.addEventListener('install', event => {
    event.waitUntil(
        (async () => {
            const cache = await caches.open(CACHE_NAME);

            // Try caching the root manually
            try {
                const response = await fetch('/');
                await cache.put('/', response.clone());
            } catch (err) {
                console.warn('Failed to cache root /', err);
            }

            console.log('Service Worker installed and cache opened:', CACHE_NAME);
            // Cache static assets
            await cache.addAll([
              '/productionRates',
              '/productionRates/data',
              '/productionRates/download_csv',
              '/motor',
              '/motor/data',
              '/motor/download_csv',
              '/senser',
              '/senser/data',
              '/senser/download_csv',
              '/iotDevices',
              '/static/app.css',
              '/static/app.js',
            ]);
        })()
    );
    self.skipWaiting(); // Force SW to activate immediately
});

self.addEventListener('activate', event => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request)
            .then(response => response)
            .catch(async () => {
                const cached = await caches.match(event.request);

                // If navigating, fallback to offline page
                if (event.request.mode === 'navigate') {
                    return caches.match(OFFLINE_URL);
                }

                return cached;
            })
    );
});

self.addEventListener('sync', event => {
    if (event.tag === 'retry-request') {
        event.waitUntil(
            fetch('/api/tryFetch').catch(() => console.log('Retry Later'))
        );
    }
});

