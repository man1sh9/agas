const CACHE_NAME = 'agas-ashram-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/index',
    '/agas_home',
    '/auth',
    '/member_profile',
    '/event_registration',
    '/assets/agas/icons/pwa-icon.png',
    'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap',
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;600;800&display=swap'
];

// Install Event
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log('Pre-caching assets');
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Activate Event
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(keys
                .filter(key => key !== CACHE_NAME)
                .map(key => caches.delete(key))
            );
        })
    );
});

// Fetch Event
self.addEventListener('fetch', event => {
    // Only cache GET requests
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request)
            .then(res => {
                // Clone response to put in cache
                const resClone = res.clone();
                caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, resClone);
                });
                return res;
            })
            .catch(() => {
                // Fallback to cache if network fails
                return caches.match(event.request);
            })
    );
});
