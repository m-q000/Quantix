import math
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.stalls.models import Stall
from apps.inspections.models import Inspection, Violation
from apps.subscriptions.models import Subscription

from .forms import InspectionForm, ViolationForm


def _officer_required(view_func):
    from functools import wraps
    from apps.accounts.models import CustomUser

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != CustomUser.ROLE_OFFICER:
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def _haversine_distance(lat1, lon1, lat2, lon2):
    """Returns distance in meters between two GPS coordinates."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


@_officer_required
def dashboard(request):
    """Officer home: today's inspection count and recent activity."""
    today = timezone.now().date()
    inspections_today = Inspection.objects.filter(
        officer=request.user,
        timestamp__date=today,
    ).count()
    recent = Inspection.objects.filter(officer=request.user).order_by('-timestamp')[:10]
    return render(request, 'officer_portal/dashboard.html', {
        'inspections_today': inspections_today,
        'recent_inspections': recent,
    })


@_officer_required
def scan(request):
    """QR scan entry point. Officers are redirected here after scanning."""
    return render(request, 'officer_portal/scan.html')


@_officer_required
def verify_stall(request, token):
    """
    Core inspection view.
    Retrieves stall by QR token, runs all four validation checks,
    and renders flags for the officer to review before recording.
    """
    stall = get_object_or_404(Stall, qr_token=token)
    now = timezone.localtime()

    # --- Validation checks ---
    # 1. Time validity
    valid_time = False
    if stall.location:
        day = now.strftime('%A').lower()
        valid_time = (
            day in stall.location.allowed_days
            and stall.location.start_time <= now.time() <= stall.location.end_time
        )

    # 2. Activity validity (category allowed at location)
    valid_activity = False
    if stall.location:
        valid_activity = stall.location.allowed_categories.filter(
            category=stall.category
        ).exists()

    # 3. Subscription validity
    valid_subscription = Subscription.objects.filter(
        stall=stall, status=Subscription.STATUS_ACTIVE,
        expiry_date__gte=now.date()
    ).exists()

    # 4. Location validity (requires officer GPS from POST)
    valid_location = False
    officer_lat = request.POST.get('latitude')
    officer_lng = request.POST.get('longitude')
    if stall.location and officer_lat and officer_lng:
        distance = _haversine_distance(
            float(officer_lat), float(officer_lng),
            float(stall.location.latitude), float(stall.location.longitude)
        )
        valid_location = distance <= stall.location.radius_meters

    form = InspectionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        inspection = form.save(commit=False)
        inspection.stall = stall
        inspection.officer = request.user
        inspection.valid_location = valid_location
        inspection.valid_time = valid_time
        inspection.valid_activity = valid_activity
        inspection.valid_subscription = valid_subscription
        inspection.officer_latitude = officer_lat or None
        inspection.officer_longitude = officer_lng or None
        inspection.save()
        return redirect('officer_portal:inspection_detail', pk=inspection.pk)

    return render(request, 'officer_portal/verify.html', {
        'stall': stall,
        'valid_location': valid_location,
        'valid_time': valid_time,
        'valid_activity': valid_activity,
        'valid_subscription': valid_subscription,
        'form': form,
        'officer_lat': officer_lat,
        'officer_lng': officer_lng,
    })


@_officer_required
def inspection_detail(request, pk):
    inspection = get_object_or_404(Inspection, pk=pk, officer=request.user)
    violation_form = ViolationForm(request.POST or None)
    if request.method == 'POST' and violation_form.is_valid():
        v = violation_form.save(commit=False)
        v.inspection = inspection
        v.stall = inspection.stall
        v.officer = request.user
        v.save()
        return redirect('officer_portal:inspection_detail', pk=pk)

    return render(request, 'officer_portal/inspection_detail.html', {
        'inspection': inspection,
        'violation_form': violation_form,
    })


@_officer_required
def inspections_list(request):
    all_inspections = Inspection.objects.filter(officer=request.user).order_by('-timestamp')
    return render(request, 'officer_portal/inspections.html', {
        'inspections': all_inspections,
    })
