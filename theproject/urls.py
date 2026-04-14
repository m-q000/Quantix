from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django built-in admin (superuser only)
    path('admin/', admin.site.urls),

    # ── Shared authentication ────────────────────────────────────────────────
    # /auth/login/   /auth/logout/   /auth/register/
    path('auth/', include('apps.accounts.urls', namespace='accounts')),

    # ── Citizen / Public portal  (root URL → map) ────────────────────────────
    path('', include('apps.public_portal.urls', namespace='public_portal')),

    # ── Vendor portal  /vendor/ ──────────────────────────────────────────────
    path('vendor/', include('apps.vendor_portal.urls', namespace='vendor_portal')),

    # ── Officer portal  /officer/ ────────────────────────────────────────────
    path('officer/', include('apps.officer_portal.urls', namespace='officer_portal')),

    # ── Municipality admin portal  /municipality/ ────────────────────────────
    path('municipality/', include('apps.municipality_portal.urls', namespace='municipality_portal')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
