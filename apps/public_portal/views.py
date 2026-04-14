import json

from django.shortcuts import get_object_or_404, render

from apps.stalls.models import Stall, StallCategory


def map_view(request):
    """
    Interactive map showing all active stalls.
    Passes stall data as JSON for Leaflet.js markers.
    """
    stalls_qs = Stall.objects.filter(status=Stall.STATUS_ACTIVE).select_related(
        'location', 'category', 'owner__user'
    )
    categories = StallCategory.objects.all()

    stalls_data = []
    for stall in stalls_qs:
        if stall.location:
            stalls_data.append({
                'id': stall.pk,
                'owner': stall.owner.user.get_full_name() or stall.owner.user.username,
                'category': stall.category.name if stall.category else '',
                'category_icon': stall.category.icon if stall.category else '',
                'lat': float(stall.location.latitude),
                'lng': float(stall.location.longitude),
                'location_name': stall.location.name,
                'start_time': stall.location.start_time.strftime('%H:%M') if stall.location.start_time else '',
                'end_time': stall.location.end_time.strftime('%H:%M') if stall.location.end_time else '',
                'allowed_days': stall.location.allowed_days or [],
                'status': stall.status,
                'is_open': stall.is_open_now(),
                'qr_token': str(stall.qr_token),
            })

    return render(request, 'public_portal/map.html', {
        'stalls': stalls_qs,
        'categories': categories,
        'stalls_json': json.dumps(stalls_data, ensure_ascii=False),
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
