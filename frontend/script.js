/**
 * Q-Zone Smart Stall MVP - Frontend Logic
 * Version 2.0 (I18N, Auth Flow, Sidebar, Search)
 */

// 1. Initial Data and Dictionary
const MAPBOX_TOKEN = 'YOUR_MAPBOX_TOKEN_HERE';
mapboxgl.accessToken = MAPBOX_TOKEN;

const HEBRON_CENTER = [35.1042, 31.5326];

// Translations Dictionary
const translations = {
    en: {
        appName: "Q-Zone",
        searchPlaceholder: "Search vendors, products, places...",
        login: "Login",
        signup: "Sign Up",
        highestRated: "Highest Rated Vendors",
        savedVendors: "Saved Vendors",
        addReview: "Add Review",
        shareStall: "Share Vendor Stall",
        aboutUs: "About Us",
        languageMode: "AR / العربية",
        bookSpot: "Book Spot",
        loginTitle: "Welcome to Q-Zone",
        loginSub: "Select an account to simulate login",
        loginCitizen: "Login as Citizen",
        loginVendor: "Login as Vendor",
        loginAdmin: "Login as Admin",
        directions: "Get Directions",
        cancel: "Cancel",
        confirmSpot: "Confirm Spot",
        zoneManagement: "Zone Management",
        createNewZone: "Create New Zone",
        spotReserved: "Spot Reserved",
        pendingQR: "Your stall location is pending validation."
    },
    ar: {
        appName: "كيو-زون",
        searchPlaceholder: "ابحث عن البائعين، المنتجات، الأماكن...",
        login: "تسجيل الدخول",
        signup: "إنشاء حساب",
        highestRated: "البائعين الأعلى تقييماً",
        savedVendors: "البائعين المحفوظين",
        addReview: "إضافة تقييم",
        shareStall: "مشاركة كشك البائع",
        aboutUs: "معلومات عنا",
        languageMode: "English / الإنجليزية",
        bookSpot: "حجز مكان",
        loginTitle: "مرحباً بك في كيو-زون",
        loginSub: "اختر حساباً لمحاكاة تسجيل الدخول",
        loginCitizen: "دخول كمواطن",
        loginVendor: "دخول كبائع",
        loginAdmin: "دخول كمسؤول",
        directions: "احصل على الاتجاهات",
        cancel: "إلغاء",
        confirmSpot: "تأكيد المكان",
        zoneManagement: "إدارة المناطق",
        createNewZone: "إنشاء منطقة جديدة",
        spotReserved: "تم حجز المكان",
        pendingQR: "موقع الكشك الخاص بك في انتظار التحقق."
    }
};

const MOCK_ZONES = [
    { id: 'zone-1', name: 'Bab Al-Zawiya', capacity: 15, occupied: 12, color: '#F59E0B', 
      polygon: [[35.102, 31.529], [35.105, 31.529], [35.106, 31.532], [35.103, 31.532], [35.102, 31.529]] },
    { id: 'zone-2', name: 'Ein Sarah St.', capacity: 20, occupied: 5, color: '#3B82F6', 
      polygon: [[35.105, 31.535], [35.108, 31.535], [35.107, 31.540], [35.104, 31.540], [35.105, 31.535]] }
];

const MOCK_VENDORS = [
    { id: 'v1', name: 'Abu Ali Falafel', type: 'Food', status: 'open', zone: 'Bab Al-Zawiya', schedule: '08:00 AM - 08:00 PM', qr: 'QR-827391', coords: [35.104, 31.530], icon: 'ri-restaurant-line', class: 'marker-food' },
    { id: 'v2', name: 'Hebron Fresh Juice', type: 'Food/Drink', status: 'open', zone: 'Bab Al-Zawiya', schedule: '10:00 AM - 10:00 PM', qr: 'QR-293847', coords: [35.1035, 31.531], icon: 'ri-goblet-line', class: 'marker-food' },
    { id: 'v3', name: 'Handcrafted Goods', type: 'Retail', status: 'closed', zone: 'Ein Sarah St.', schedule: '09:00 AM - 05:00 PM', qr: 'QR-554122', coords: [35.106, 31.537], icon: 'ri-shopping-bag-3-line', class: 'marker-goods' }
];

// App State
const state = {
    lang: localStorage.getItem('qzone_lang') || 'en',
    mode: 'guest', // guest | citizen | vendor | admin
    searchQuery: ''
};

// 2. Map Initialization (Fixing the blank map issue by ensuring window load trigger)
let map, markers = [];

function initMap() {
    map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/light-v11',
        center: HEBRON_CENTER,
        zoom: 14.5,
        pitch: 45,
        bearing: -17.6
    });

    map.on('load', () => {
        // Trigger resize to fix layout bugs
        map.resize();
        
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
    });

    // Handle Vendor Booking clicks
    let tempMarker = null;
    map.on('click', (e) => {
        if (state.mode === 'vendor') {
            if (tempMarker) tempMarker.remove();
            
            const el = document.createElement('div');
            el.className = `custom-marker`;
            el.style.borderColor = 'var(--text-main)';
            el.style.backgroundColor = 'var(--text-main)';
            el.style.color = 'white';
            el.innerHTML = `<i class="ri-map-pin-add-line"></i>`;
            
            tempMarker = new mapboxgl.Marker(el).setLngLat(e.lngLat).addTo(map);
            map.flyTo({ center: e.lngLat, zoom: 16 });
            
            showVendorBooking();
        }
    });
}

// 3. i18n Language Toggle System
function applyLanguage() {
    const isAr = state.lang === 'ar';
    document.documentElement.lang = state.lang;
    document.documentElement.dir = isAr ? 'rtl' : 'ltr';
    
    // Update Text
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if(translations[state.lang][key]) el.textContent = translations[state.lang][key];
    });
    
    // Update Placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if(translations[state.lang][key]) el.placeholder = translations[state.lang][key];
    });

    // Save to LocalStorage
    localStorage.setItem('qzone_lang', state.lang);
}

document.getElementById('lang-toggle-btn').addEventListener('click', () => {
    state.lang = state.lang === 'en' ? 'ar' : 'en';
    applyLanguage();
});


// 4. Mode Assignment & Auth
const uiElems = {
    authContainer: document.getElementById('auth-container'),
    userProfile: document.getElementById('user-profile'),
    fab: document.getElementById('main-fab'),
    overlay: document.getElementById('ui-overlay'),
    authModal: document.getElementById('auth-modal'),
    sidebar: document.getElementById('side-menu'),
    bottomSheet: document.getElementById('bottom-sheet'),
    sheetContent: document.getElementById('sheet-content')
};

function assignMode(mode) {
    state.mode = mode;
    closeModals();
    
    if (mode === 'guest') {
        uiElems.authContainer.classList.remove('hidden');
        uiElems.userProfile.classList.add('hidden');
        uiElems.fab.classList.add('hidden');
    } else {
        uiElems.authContainer.classList.add('hidden');
        uiElems.userProfile.classList.remove('hidden');
        
        if (mode === 'vendor') {
            uiElems.fab.classList.remove('hidden');
            uiElems.userProfile.querySelector('#avatar-circle').innerText = 'VN';
        } else if (mode === 'admin') {
            uiElems.fab.classList.add('hidden');
            uiElems.userProfile.querySelector('#avatar-circle').innerText = 'AD';
            showAdminPanel();
        } else { // citizen
            uiElems.fab.classList.add('hidden');
            uiElems.userProfile.querySelector('#avatar-circle').innerText = 'CT';
        }
    }
}


// Auth Listeners
document.getElementById('login-btn').addEventListener('click', () => showAuthModal('login'));
document.getElementById('signup-btn').addEventListener('click', () => showAuthModal('signup'));
document.querySelector('.close-modal').addEventListener('click', closeModals);
document.querySelectorAll('.auth-simulate').forEach(btn => {
    btn.addEventListener('click', (e) => {
        assignMode(e.currentTarget.getAttribute('data-role'));
    });
});

function showAuthModal() {
    uiElems.overlay.classList.remove('hidden');
    uiElems.authModal.classList.remove('hidden');
}


// 5. Sidebar Navigation (Hamburger)
document.getElementById('hamburger-btn').addEventListener('click', () => {
    uiElems.overlay.classList.remove('hidden');
    uiElems.sidebar.classList.remove('hidden');
});

document.getElementById('close-menu-btn').addEventListener('click', closeModals);
uiElems.overlay.addEventListener('click', closeModals);

function closeModals() {
    uiElems.overlay.classList.add('hidden');
    uiElems.sidebar.classList.add('hidden');
    uiElems.authModal.classList.add('hidden');
}


// 6. Search Bar System
const searchInput = document.getElementById('search-input');
const clearSearchBtn = document.getElementById('clear-search');

searchInput.addEventListener('input', (e) => {
    const val = e.target.value.trim().toLowerCase();
    state.searchQuery = val;
    val.length > 0 ? clearSearchBtn.classList.remove('hidden') : clearSearchBtn.classList.add('hidden');
    
    renderMarkers(); // Re-render markers with search filter
});

clearSearchBtn.addEventListener('click', () => {
    searchInput.value = '';
    state.searchQuery = '';
    clearSearchBtn.classList.add('hidden');
    renderMarkers();
});


// 7. Render Routines (Map)
function renderZones() {
    MOCK_ZONES.forEach(zone => {
        map.addSource(zone.id, {
            'type': 'geojson',
            'data': { 'type': 'Feature', 'geometry': { 'type': 'Polygon', 'coordinates': [zone.polygon] } }
        });
        map.addLayer({ 'id': `${zone.id}-fill`, 'type': 'fill', 'source': zone.id, 'paint': { 'fill-color': zone.color, 'fill-opacity': 0.15 }});
        map.addLayer({ 'id': `${zone.id}-outline`, 'type': 'line', 'source': zone.id, 'paint': { 'line-color': zone.color, 'line-width': 2, 'line-dasharray': [2, 2] }});
    });
}

function renderMarkers() {
    // Clear old markers
    markers.forEach(m => m.remove());
    markers = [];
    
    // Filter logic
    const filtered = MOCK_VENDORS.filter(v => {
        if (!state.searchQuery) return true;
        return v.name.toLowerCase().includes(state.searchQuery) || 
               v.type.toLowerCase().includes(state.searchQuery) ||
               v.zone.toLowerCase().includes(state.searchQuery);
    });

    filtered.forEach(vendor => {
        const el = document.createElement('div');
        el.className = `custom-marker ${vendor.class}`;
        el.innerHTML = `<i class="${vendor.icon}"></i>`;
        
        el.addEventListener('click', (e) => {
            e.stopPropagation();
            showVendorDetails(vendor);
        });

        const marker = new mapboxgl.Marker(el)
            .setLngLat(vendor.coords)
            .addTo(map);
        markers.push(marker);
    });
}

// 8. Bottom Sheet Displays
function showVendorDetails(vendor) {
    uiElems.sheetContent.innerHTML = `
        <div class="vendor-card" style="padding-top:16px;">
            <div class="card-header">
                <div>
                    <h2>${vendor.name}</h2>
                    <span class="text-muted">${vendor.type} • ${vendor.zone}</span>
                </div>
                <div class="badge ${vendor.status}">${vendor.status.toUpperCase()}</div>
            </div>
            <div class="details-list" style="margin-top:16px;">
                <div class="detail-row">
                    <i class="ri-time-line"></i><span>${vendor.schedule}</span>
                </div>
                <div class="detail-row">
                    <i class="ri-qr-code-line"></i><span>ID: ${vendor.qr} <a href="#" style="font-size:0.8rem; margin-left:8px">(Report)</a></span>
                </div>
            </div>
            <button class="btn-primary" style="width:100%; margin-top:16px;">
                <i class="ri-direction-line"></i> <span data-i18n="directions">${translations[state.lang].directions}</span>
            </button>
        </div>
    `;
    uiElems.bottomSheet.classList.remove('hidden');
}

function showVendorBooking() {
    uiElems.sheetContent.innerHTML = `
        <div class="booking-card" style="padding-top:16px;">
            <div class="card-header">
                <div>
                    <h2 data-i18n="bookSpot">${translations[state.lang].bookSpot}</h2>
                    <span class="text-muted">Select zone to attach your stall</span>
                </div>
            </div>
            <div style="display:flex; gap:8px; margin: 16px 0;">
                <button class="btn-secondary" style="border: 2px solid var(--warning)">Bab Al-Zawiya</button>
                <button class="btn-secondary">Ein Sarah</button>
            </div>
            <div class="detail-row">
                <i class="ri-calendar-event-line"></i>
                <span style="flex-grow:1">Today, 08:00 AM - 06:00 PM</span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:16px;">
                <button class="btn-secondary" onclick="document.getElementById('bottom-sheet').classList.add('hidden')">${translations[state.lang].cancel}</button>
                <button class="btn-primary" onclick="confirmBooking()">${translations[state.lang].confirmSpot}</button>
            </div>
        </div>
    `;
    uiElems.bottomSheet.classList.remove('hidden');
}

window.confirmBooking = function() {
    uiElems.sheetContent.innerHTML = `
        <div style="text-align:center; padding: 24px 0">
            <div style="width:64px; height:64px; border-radius:50%; background:var(--success); color:white; display:grid; place-items:center; font-size:2rem; margin:0 auto 16px;">
                <i class="ri-check-line"></i>
            </div>
            <h2 data-i18n="spotReserved">${translations[state.lang].spotReserved}</h2>
            <p class="text-muted" style="margin-bottom:24px" data-i18n="pendingQR">${translations[state.lang].pendingQR}</p>
            <button class="btn-primary" style="width:100%" onclick="document.getElementById('bottom-sheet').classList.add('hidden')">Done</button>
        </div>
    `;
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

    uiElems.sheetContent.innerHTML = `
        <div class="zone-card" style="padding-top:16px;">
            <div class="card-header">
                <div>
                    <h2 data-i18n="zoneManagement">${translations[state.lang].zoneManagement}</h2>
                    <span class="text-muted">Active regulatory areas</span>
                </div>
            </div>
            <div style="margin-top:16px">${zonesHtml}</div>
            <button class="btn-primary" style="width:100%; margin-top:16px"><i class="ri-add-line" style="margin-right:8px"></i> <span data-i18n="createNewZone">${translations[state.lang].createNewZone}</span></button>
        </div>
    `;
    uiElems.bottomSheet.classList.remove('hidden');
    map.flyTo({ center: HEBRON_CENTER, zoom: 14.5, pitch: 0 });
}

// 9. Startup Sequence
window.addEventListener('DOMContentLoaded', () => {
    applyLanguage();
    assignMode('guest'); // Implicitly starts as citizen/view-only
    initMap();
});
