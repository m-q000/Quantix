from django.shortcuts import get_object_or_404, render

from apps.stalls.models import Stall, StallCategory


def map_view(request):
    """
    Interactive map showing all active stalls.
    Passes stall data as JSON context for Leaflet.js markers.
    """
    stalls = Stall.objects.filter(status=Stall.STATUS_ACTIVE).select_related(
        'location', 'category'
    )
    categories = StallCategory.objects.all()
    return render(request, 'public_portal/map.html', {
        'stalls': stalls,
        'categories': categories,
    })


def stall_detail(request, stall_id):
    """Public stall detail page: images, schedule, open/closed status."""
    stall = get_object_or_404(Stall, pk=stall_id, status=Stall.STATUS_ACTIVE)
    return render(request, 'public_portal/stall_detail.html', {
        'stall': stall,
        'is_open': stall.is_open_now(),
    })


def verify_qr(request, token):
    """
    QR code landing page. Behavior differs by viewer role:
    - Anonymous / Citizen → stall info card
    - Officer → full validation dashboard (location, time, activity, subscription flags)
    """
    stall = get_object_or_404(Stall, qr_token=token)

    # Officers get a richer validation view
    if request.user.is_authenticated and request.user.is_officer():
        return render(request, 'public_portal/verify_qr_officer.html', {'stall': stall})

    return render(request, 'public_portal/verify_qr_public.html', {'stall': stall})


def report_violation(request, stall_id):
    """Citizen can submit a report on a stall (abuse, wrong location, etc.)."""
    from apps.notifications.models import Notification
    from apps.accounts.models import CustomUser

    stall = get_object_or_404(Stall, pk=stall_id)
    if request.method == 'POST':
        # Notify all municipality admins
        admins = CustomUser.objects.filter(role=CustomUser.ROLE_ADMIN)
        for admin in admins:
            Notification.objects.create(
                recipient=admin,
                notification_type=Notification.TYPE_NEW_REPORT,
                title=f"Citizen report on stall #{stall.pk}",
                message=request.POST.get('message', ''),
            )
        return render(request, 'public_portal/report_sent.html', {'stall': stall})

    return render(request, 'public_portal/report_violation.html', {'stall': stall})
