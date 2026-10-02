import re

def update_app_py():
    with open("src/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add PWA manifest link and theme-color in <head>
    old_head = '<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">'
    new_head = '''<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#0f172a">'''

    if old_head in content:
        content = content.replace(old_head, new_head, 1) # replace in INDEX_HTML head
        print("Added PWA manifest link to <head>!")
    else:
        print("Could not find old_head in app.py!")

    # 2. Add Network Status Badge to Header
    old_header_badges = '<div class="table-badge d-flex align-items-center gap-2">\n                        <i class="fa-solid fa-qrcode"></i>\n                        <span>Table #<span id="activeTableBadgeNum">1</span></span>\n                    </div>'
    new_header_badges = '''<div class="table-badge d-flex align-items-center gap-2">
                        <i class="fa-solid fa-qrcode"></i>
                        <span>Table #<span id="activeTableBadgeNum">1</span></span>
                    </div>
                    <span id="pwaNetworkBadge" class="badge bg-success rounded-pill px-3 py-2 ms-2"><i class="fa-solid fa-wifi me-1"></i> Online</span>'''

    if old_header_badges in content:
        content = content.replace(old_header_badges, new_header_badges)
        print("Added pwaNetworkBadge to Header!")
    else:
        print("Could not find old_header_badges in app.py!")

    # 3. Add Offline Sync Banner in Main section
    old_banner = '<div id="waiterAlertBanner" class="alert alert-success alert-dismissible fade show d-none shadow-sm rounded-3" role="alert">'
    new_banner = '''<div id="offlineSyncBanner" class="alert alert-warning border-warning shadow-sm rounded-3 d-none mb-3" role="alert">
            <div class="d-flex align-items-center justify-content-between">
                <div>
                    <i class="fa-solid fa-wifi-slash text-danger me-2 fs-5"></i>
                    <strong>Offline Dining Mode (Dead-Zone Protection)</strong>
                    <div class="small text-dark">You are offline. Orders are saved securely on device and will auto-sync when connection resumes.</div>
                </div>
                <span class="badge bg-dark text-warning fs-6 px-3 py-2 rounded-pill" id="offlinePendingCountBadge">0 Pending</span>
            </div>
        </div>
        <div id="waiterAlertBanner" class="alert alert-success alert-dismissible fade show d-none shadow-sm rounded-3" role="alert">'''

    if old_banner in content:
        content = content.replace(old_banner, new_banner)
        print("Added offlineSyncBanner HTML!")
    else:
        print("Could not find old_banner in app.py!")

    # 4. Add Service Worker registration and PWA sync JS handlers before script tag end
    pwa_js_code = '''
        // --- PWA Service Worker & Offline Sync Queue ---
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js')
                    .then(reg => console.log('PWA Service Worker registered:', reg.scope))
                    .catch(err => console.error('PWA Service Worker registration failed:', err));
            });
        }

        function updateNetworkStatus() {
            const badge = document.getElementById('pwaNetworkBadge');
            const banner = document.getElementById('offlineSyncBanner');
            const isOnline = navigator.onLine;

            if (badge) {
                if (isOnline) {
                    badge.className = 'badge bg-success rounded-pill px-3 py-2 ms-2';
                    badge.innerHTML = '<i class="fa-solid fa-wifi me-1"></i> Online';
                } else {
                    badge.className = 'badge bg-danger rounded-pill px-3 py-2 ms-2';
                    badge.innerHTML = '<i class="fa-solid fa-wifi-slash me-1"></i> Offline';
                }
            }

            if (banner) {
                if (!isOnline) {
                    banner.classList.remove('d-none');
                } else {
                    banner.classList.add('d-none');
                    syncOfflineQueue();
                }
            }
            updateOfflinePendingBadge();
        }

        function getOfflineQueue() {
            try {
                return JSON.parse(localStorage.getItem('waiter_offline_orders') || '[]');
            } catch(e) {
                return [];
            }
        }

        function saveOfflineQueue(queue) {
            localStorage.setItem('waiter_offline_orders', JSON.stringify(queue));
            updateOfflinePendingBadge();
        }

        function updateOfflinePendingBadge() {
            const queue = getOfflineQueue();
            const badge = document.getElementById('offlinePendingCountBadge');
            if(badge) {
                badge.innerText = queue.length + ' Pending';
            }
        }

        async function saveOrderOffline(orderPayload) {
            const queue = getOfflineQueue();
            queue.push({
                payload: orderPayload,
                timestamp: new Date().toISOString()
            });
            saveOfflineQueue(queue);
            alert('📱 [Offline PWA] Order saved locally on device! It will auto-submit as soon as Wi-Fi reconnects.');
        }

        async function syncOfflineQueue() {
            const queue = getOfflineQueue();
            if (queue.length === 0) return;

            console.log(`Syncing ${queue.length} offline orders...`);
            let syncedCount = 0;
            const remainingQueue = [];

            for (const item of queue) {
                try {
                    const res = await fetch('/api/order', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(item.payload)
                    });
                    if (res.ok) {
                        syncedCount++;
                    } else {
                        remainingQueue.push(item);
                    }
                } catch(e) {
                    remainingQueue.push(item);
                }
            }

            saveOfflineQueue(remainingQueue);

            if (syncedCount > 0) {
                alert(`🚀 [PWA Auto-Sync] Successfully synced ${syncedCount} offline order(s) to the kitchen!`);
                loadTableLiveOrderStatus();
            }
        }

        window.addEventListener('online', updateNetworkStatus);
        window.addEventListener('offline', updateNetworkStatus);
'''

    target_script_end = "    </script>\n</body>\n</html>\"\"\""
    if target_script_end in content:
        content = content.replace(target_script_end, pwa_js_code + "\n" + target_script_end)
        print("Added PWA JS functions before script end!")
    else:
        print("Could not find target_script_end in app.py!")

    # 5. Add backend PWA routes (/manifest.json and /sw.js)
    pwa_backend_routes = '''
# --- 21. PWA & Service Worker Endpoints ---
@app.route("/manifest.json", methods=["GET"])
def pwa_manifest():
    manifest = {
        "name": "The Waiter — Digital Hospitality Platform",
        "short_name": "The Waiter",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#0f172a",
        "orientation": "any",
        "icons": [
            {
                "src": "https://cdn-icons-png.flaticon.com/512/3448/3448609.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "https://cdn-icons-png.flaticon.com/512/3448/3448609.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return jsonify(manifest)

@app.route("/sw.js", methods=["GET"])
def pwa_service_worker():
    sw_code = """
const CACHE_NAME = 'waiter-pwa-cache-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/manifest.json',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS_TO_CACHE))
    );
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys.map(key => {
                if (key !== CACHE_NAME) return caches.delete(key);
            })
        ))
    );
    self.clients.claim();
});

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;
    event.respondWith(
        fetch(event.request)
            .then(networkResponse => {
                if (networkResponse && networkResponse.status === 200) {
                    const resClone = networkResponse.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, resClone));
                }
                return networkResponse;
            })
            .catch(() => caches.match(event.request))
    );
});
"""
    return Response(sw_code, mimetype="application/javascript")
'''

    main_block = 'if __name__ == "__main__":'
    if main_block in content:
        content = content.replace(main_block, pwa_backend_routes + "\n\n" + main_block)
        print("Added backend routes /manifest.json and /sw.js!")
    else:
        print("Could not find main_block in app.py!")

    with open("src/app.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_app_py()
