/**
 * Q-Zone Smart Stall MVP - Frontend Logic
 * Implements Mapbox GL JS map with 3 user flows: Citizen, Vendor, Admin.
 */

// 1. Initial Data and Mapbox Setup
const MAPBOX_TOKEN = 'YOUR_MAPBOX_TOKEN_HERE'; // Public default mapbox token for testing
mapboxgl.accessToken = MAPBOX_TOKEN;

// Hebron Coordinates
const HEBRON_CENTER = [35.1042, 31.5326];

// Mock Data
const MOCK_ZONES = [
    {
        id: 'zone-1',
        name: 'Bab Al-Zawiya',
        capacity: 15,
        occupied: 12,
        color: '#F59E0B',
        polygon: [
            [35.102, 31.529], [35.105, 31.529], 
            [35.106, 31.532], [35.103, 31.532],
            [35.102, 31.529]
        ]
    },
    {
        id: 'zone-2',
        name: 'Ein Sarah St.',
        capacity: 20,
        occupied: 5,
        color: '#3B82F6',
        polygon: [
            [35.105, 31.535], [35.108, 31.535], 
            [35.107, 31.540], [35.104, 31.540],
            [35.105, 31.535]
        ]
    }
];

const MOCK_VENDORS = [
    {
        id: 'v1',
        name: 'Abu Ali Falafel',
        type: 'Food',
        status: 'open',
        zone: 'Bab Al-Zawiya',
        schedule: '08:00 AM - 08:00 PM',
        qr: 'QR-827391',
        coords: [35.104, 31.530],
        icon: 'ri-restaurant-line',
        class: 'marker-food'
    },
    {
        id: 'v2',
        name: 'Hebron Fresh Juice',
        type: 'Food/Drink',
        status: 'open',
        zone: 'Bab Al-Zawiya',
        schedule: '10:00 AM - 10:00 PM',
        qr: 'QR-293847',
        coords: [35.1035, 31.531],
        icon: 'ri-goblet-line',
        class: 'marker-food'
    },
    {
        id: 'v3',
        name: 'Handcrafted Goods',
        type: 'Retail',
        status: 'closed',
        zone: 'Ein Sarah St.',
        schedule: '09:00 AM - 05:00 PM',
        qr: 'QR-554122',
        coords: [35.106, 31.537],
        icon: 'ri-shopping-bag-3-line',
        class: 'marker-goods'
    }
];

// App State
const state = {
    mode: 'citizen', // citizen | vendor | admin
    activeMarkerId: null,
    vendorSelectedCoords: null,
};

// 2. Map Initialization
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/light-v11', // Clean, high-contrast light style
    center: HEBRON_CENTER,
    zoom: 14.5,
    pitch: 45, // Add some 3D feel
    bearing: -17.6
});

let markers = [];

map.on('load', () => {
    // Add 3D Buildings
    map.addLayer({
        'id': '3d-buildings',
        'source': 'composite',
        'source-layer': 'building',
        'filter': ['==', 'extrude', 'true'],
        'type': 'fill-extrusion',
        'minzoom': 15,
        'paint': {
            'fill-extrusion-color': '#eef0f2',
            'fill-extrusion-height': ['get', 'height'],
            'fill-extrusion-base': ['get', 'min_height'],
            'fill-extrusion-opacity': 0.8
        }
    });

    renderZones();
    renderMarkers();
    switchMode('citizen');
});

// 3. Rendering Layers
function renderZones() {
    MOCK_ZONES.forEach(zone => {
        map.addSource(zone.id, {
            'type': 'geojson',
            'data': {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [zone.polygon]
                }
            }
        });

        // Fill
        map.addLayer({
            'id': `${zone.id}-fill`,
            'type': 'fill',
            'source': zone.id,
            'layout': {},
            'paint': {
                'fill-color': zone.color,
                'fill-opacity': 0.15
            }
        });

        // Outline
        map.addLayer({
            'id': `${zone.id}-outline`,
            'type': 'line',
            'source': zone.id,
            'layout': {},
            'paint': {
                'line-color': zone.color,
                'line-width': 2,
                'line-dasharray': [2, 2]
            }
        });
    });
}

function renderMarkers() {
    clearMarkers();
    
    if (state.mode === 'vendor') return; // Hide standard markers in vendor booking mode

    MOCK_VENDORS.forEach(vendor => {
        const el = document.createElement('div');
        el.className = `custom-marker ${vendor.class}`;
        el.innerHTML = `<i class="${vendor.icon}"></i>`;
        
        el.addEventListener('click', (e) => {
            e.stopPropagation(); // prevent map click execution
            showVendorDetails(vendor);
        });

        const marker = new mapboxgl.Marker(el)
            .setLngLat(vendor.coords)
            .addTo(map);
            
        markers.push(marker);
    });
}

function clearMarkers() {
    markers.forEach(m => m.remove());
    markers = [];
}

// 4. UI Interactions & Mode Switching
const uiElements = {
    modeBtns: document.querySelectorAll('.mode-btn'),
    bottomSheet: document.getElementById('bottom-sheet'),
    sheetContent: document.getElementById('sheet-content'),
    fab: document.getElementById('main-fab'),
    statusPill: document.getElementById('status-pill'),
    dot: document.querySelector('.brand .dot')
};

uiElements.modeBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        uiElements.modeBtns.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        switchMode(e.target.dataset.mode);
    });
});

function switchMode(mode) {
    state.mode = mode;
    hideSheet();
    
    // Style adjustments per mode
    if (mode === 'citizen') {
        uiElements.dot.className = 'dot active';
        uiElements.fab.classList.add('hidden');
        uiElements.statusPill.classList.add('hidden');
        renderMarkers();
    } else if (mode === 'vendor') {
        uiElements.dot.className = 'dot';
        uiElements.dot.style.background = 'var(--warning)';
        uiElements.fab.classList.remove('hidden');
        uiElements.fab.querySelector('span').innerText = 'Book Spot';
        uiElements.statusPill.classList.add('hidden');
        renderMarkers(); 
    } else if (mode === 'admin') {
        uiElements.dot.className = 'dot';
        uiElements.dot.style.background = 'var(--text-main)';
        uiElements.fab.classList.add('hidden');
        uiElements.statusPill.classList.add('hidden');
        renderMarkers();
        showAdminPanel();
    }
}

// Map Click Handler (for Vendor booking)
let tempMarker = null;
map.on('click', (e) => {
    if (state.mode === 'vendor') {
        state.vendorSelectedCoords = e.lngLat;
        
        if (tempMarker) tempMarker.remove();
        
        const el = document.createElement('div');
        el.className = `custom-marker`;
        el.style.borderColor = 'var(--text-main)';
        el.style.backgroundColor = 'var(--text-main)';
        el.style.color = 'white';
        el.innerHTML = `<i class="ri-map-pin-add-line"></i>`;
        
        tempMarker = new mapboxgl.Marker(el)
            .setLngLat(e.lngLat)
            .addTo(map);
            
        // Fly to
        map.flyTo({ center: e.lngLat, zoom: 16 });
        
        // Show Booking Sheet
        showVendorBooking();
    }
});

// 5. Dynamic Views
function showVendorDetails(vendor) {
    uiElements.sheetContent.innerHTML = `
        <div class="vendor-card">
            <div class="card-header">
                <div>
                    <h2>${vendor.name}</h2>
                    <span class="card-subtitle">${vendor.type} • ${vendor.zone}</span>
                </div>
                <div class="badge ${vendor.status}">${vendor.status.toUpperCase()}</div>
            </div>
            
            <div class="details-list">
                <div class="detail-row">
                    <i class="ri-time-line"></i>
                    <span>${vendor.schedule}</span>
                </div>
                <div class="detail-row">
                    <i class="ri-qr-code-line"></i>
                    <span>ID: ${vendor.qr} <a href="#" style="color:var(--text-muted); font-size: 0.8rem; margin-left:8px">(Report Issue)</a></span>
                </div>
            </div>
            
            <button class="btn-primary" style="width:100%; margin-top:8px">
                <i class="ri-direction-line" style="margin-right:8px"></i> Get Directions
            </button>
        </div>
    `;
    uiElements.bottomSheet.classList.remove('hidden');
    map.flyTo({ center: vendor.coords, zoom: 16, offset: [0, 100] });
}

function showVendorBooking() {
    uiElements.sheetContent.innerHTML = `
        <div class="booking-card">
            <div class="card-header">
                <div>
                    <div class="badge zone" style="margin-bottom:8px; display:inline-block">NEW STALL</div>
                    <h2>Book this location</h2>
                    <span class="card-subtitle">Select a zone parameter to confirm</span>
                </div>
            </div>
            
            <div class="zone-selector">
                <button class="zone-pill selected">Bab Al-Zawiya</button>
                <button class="zone-pill">Ein Sarah</button>
                <button class="zone-pill">Other</button>
            </div>

            <div class="detail-row">
                <i class="ri-calendar-event-line"></i>
                <span style="flex-grow:1">Today, 08:00 AM - 06:00 PM</span>
                <i class="ri-arrow-right-s-line"></i>
            </div>
            
            <div class="action-grid">
                <button class="btn-secondary" onclick="hideSheet()">Cancel</button>
                <button class="btn-primary" onclick="confirmBooking()">Confirm Spot</button>
            </div>
        </div>
    `;
    uiElements.bottomSheet.classList.remove('hidden');
}

window.confirmBooking = function() {
    uiElements.sheetContent.innerHTML = `
        <div class="booking-card" style="text-align:center; padding: 24px 0">
            <div style="width:64px; height:64px; border-radius:50%; background:var(--success); color:white; display:grid; place-items:center; font-size:2rem; margin:0 auto 16px;">
                <i class="ri-check-line"></i>
            </div>
            <h2>Spot Reserved</h2>
            <p class="card-subtitle" style="margin-bottom:24px">Your stall location is pending QR generated validation.</p>
            <button class="btn-primary" style="width:100%" onclick="switchMode('citizen')">Done</button>
        </div>
    `;
    if(tempMarker) tempMarker.remove();
}

function showAdminPanel() {
    let zonesHtml = MOCK_ZONES.map(z => `
        <div class="detail-row" style="justify-content:space-between">
            <div style="display:flex; align-items:center; gap:12px">
                <div style="width:12px; height:12px; border-radius:50%; background:${z.color}"></div>
                <div>
                    <div style="font-weight:600">${z.name}</div>
                    <div style="font-size:0.8rem; color:var(--text-muted)">${z.occupied}/${z.capacity} Slots Full</div>
                </div>
            </div>
            <button class="btn-secondary" style="padding:6px 12px; font-size:0.85rem">Edit</button>
        </div>
    `).join('');

    uiElements.sheetContent.innerHTML = `
        <div class="zone-card">
            <div class="card-header">
                <div>
                    <h2>Zone Management</h2>
                    <span class="card-subtitle">Active regulatory areas</span>
                </div>
            </div>
            <div style="margin-top:8px">${zonesHtml}</div>
            <button class="btn-primary" style="width:100%; margin-top:16px"><i class="ri-add-line" style="margin-right:8px"></i> Create New Zone</button>
        </div>
    `;
    uiElements.bottomSheet.classList.remove('hidden');
    map.flyTo({ center: HEBRON_CENTER, zoom: 14.5, pitch: 0 });
}

function hideSheet() {
    uiElements.bottomSheet.classList.add('hidden');
}

// Global UI handling
uiElements.fab.addEventListener('click', () => {
    uiElements.statusPill.classList.remove('hidden');
});
