// ═══════════════════════════════════════════════
// Scuderia Pit-Wall — Service Worker
// Cache strategy: network-first for API calls,
// cache-first for static assets
// ═══════════════════════════════════════════════

const CACHE_NAME = 'pitwall-v1';
const STATIC_CACHE = 'pitwall-static-v1';
const API_CACHE = 'pitwall-api-v1';

// Assets to cache immediately on install
const PRECACHE_ASSETS = [
  '/',
  '',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  'https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Barlow+Condensed:wght@600;700;800;900&display=swap',
  'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap'
];

// API endpoints — network-first, fallback to cache
const API_ROUTES = [
  '/process',
  '/health',
  '/audit'
];

// ── INSTALL ──────────────────────────────────────
self.addEventListener('install', (event) => {
  console.log('[Pit-Wall SW] Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      console.log('[Pit-Wall SW] Pre-caching static assets');
      // Use addAll with individual error handling to avoid
      // one failed asset blocking the whole install
      return Promise.allSettled(
        PRECACHE_ASSETS.map(url =>
          cache.add(url).catch(err =>
            console.warn(`[Pit-Wall SW] Failed to cache: ${url}`, err)
          )
        )
      );
    }).then(() => {
      console.log('[Pit-Wall SW] Install complete');
      return self.skipWaiting();
    })
  );
});

// ── ACTIVATE ─────────────────────────────────────
self.addEventListener('activate', (event) => {
  console.log('[Pit-Wall SW] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter(name => name !== STATIC_CACHE && name !== API_CACHE)
          .map(name => {
            console.log(`[Pit-Wall SW] Deleting old cache: ${name}`);
            return caches.delete(name);
          })
      );
    }).then(() => {
      console.log('[Pit-Wall SW] Activation complete — controlling all clients');
      return self.clients.claim();
    })
  );
});

// ── FETCH ─────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests (POST to /process etc.)
  // These must always hit the network — IBM Watson calls
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome-extension and non-http requests
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // API routes — network-first, cache fallback
  if (API_ROUTES.some(route => url.pathname.startsWith(route))) {
    event.respondWith(networkFirstStrategy(request, API_CACHE));
    return;
  }

  // Static assets — cache-first, network fallback
  event.respondWith(cacheFirstStrategy(request, STATIC_CACHE));
});

// ── STRATEGIES ────────────────────────────────────

// Network-first: try network, fall back to cache
// Used for API health checks and audit logs
async function networkFirstStrategy(request, cacheName) {
  const cache = await caches.open(cacheName);
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('[Pit-Wall SW] Network failed, serving from cache:', request.url);
    const cachedResponse = await cache.match(request);
    if (cachedResponse) return cachedResponse;
    return offlineFallback(request);
  }
}

// Cache-first: serve from cache, update in background
// Used for fonts, icons, and HTML shell
async function cacheFirstStrategy(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);

  if (cachedResponse) {
    // Revalidate in background (stale-while-revalidate)
    fetch(request).then(networkResponse => {
      if (networkResponse.ok) {
        cache.put(request, networkResponse.clone());
      }
    }).catch(() => {});
    return cachedResponse;
  }

  // Not in cache — fetch and store
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    return offlineFallback(request);
  }
}

// Offline fallback page
function offlineFallback(request) {
  const url = new URL(request.url);

  // Return cached shell for navigation requests
  if (request.mode === 'navigate') {
    return caches.match('/').then(response => response || new Response(
      `<!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="utf-8"/>
        <title>Pit-Wall — Offline</title>
        <style>
          body { background:#0e0a09; color:#f5ede8; font-family:'JetBrains Mono',monospace;
                 display:flex; flex-direction:column; align-items:center; justify-content:center;
                 height:100vh; gap:16px; margin:0; }
          .red { color:#dc0000; font-size:48px; font-weight:900; letter-spacing:0.06em; }
          .dim { color:#8a6f68; font-size:11px; letter-spacing:0.15em; text-transform:uppercase; }
          .dot { width:8px; height:8px; border-radius:50%; background:#dc0000;
                 animation: pulse 1s ease-in-out infinite; }
          @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.2} }
        </style>
      </head>
      <body>
        <div class="dot"></div>
        <div class="red">PIT-WALL</div>
        <div class="dim">Connection lost — race telemetry unavailable</div>
        <div class="dim">Reconnect to resume IBM watsonx pipeline</div>
      </body>
      </html>`,
      { headers: { 'Content-Type': 'text/html' } }
    ));
  }

  // For API requests, return a JSON error
  if (url.pathname.startsWith('/process') || url.pathname.startsWith('/health')) {
    return new Response(
      JSON.stringify({
        error: 'offline',
        message: 'Pit-Wall is offline. IBM watsonx pipeline unavailable.',
        output_type: 'offline'
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }

  return new Response('Offline', { status: 503 });
}

// ── BACKGROUND SYNC ──────────────────────────────
// Queue voice queries made offline and replay when reconnected
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-queries') {
    console.log('[Pit-Wall SW] Syncing queued queries...');
    event.waitUntil(syncQueuedQueries());
  }
});

async function syncQueuedQueries() {
  // Placeholder — implement with IndexedDB queue
  // to replay POST /process requests made while offline
  console.log('[Pit-Wall SW] Query sync complete');
}

// ── PUSH NOTIFICATIONS ───────────────────────────
// Future: push race alerts (safety car, pit window open, etc.)
self.addEventListener('push', (event) => {
  if (!event.data) return;
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title || 'Pit-Wall Alert', {
      body: data.body || '',
      icon: '/static/icons/icon-192.png',
      badge: '/static/icons/icon-192.png',
      tag: 'pitwall-alert',
      data: { url: data.url || '/' }
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url || '/')
  );
});
