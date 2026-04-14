from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.accounts.models import CustomUser, VendorProfile, OfficerProfile
from apps.stalls.models import Stall, StallCategory
from apps.locations.models import Location
from apps.subscriptions.models import Subscription
from apps.inspections.models import Inspection, Violation
from apps.notifications.models import Notification

from .forms import (
    LocationForm, OfficerCreationForm, StallApprovalForm,
    StallAssignLocationForm, SubscriptionForm,
)


def _admin_required(view_func):
    from functools import wraps

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != CustomUser.ROLE_ADMIN:
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── Dashboard ───────────────────────────────────────────────────────────────

@_admin_required
def dashboard(request):
    context = {
        'total_stalls': Stall.objects.count(),
        'active_stalls': Stall.objects.filter(status=Stall.STATUS_ACTIVE).count(),
        'pending_stalls': Stall.objects.filter(status=Stall.STATUS_PENDING).count(),
        'total_vendors': VendorProfile.objects.count(),
        'total_officers': OfficerProfile.objects.count(),
        'total_violations': Violation.objects.count(),
        'recent_applications': Stall.objects.filter(
            status=Stall.STATUS_PENDING
        ).order_by('-created_at')[:5],
    }
    return render(request, 'municipality_portal/dashboard.html', context)


# ── Stall Management ────────────────────────────────────────────────────────

@_admin_required
def stall_list(request):
    stalls = Stall.objects.select_related('owner__user', 'location', 'category').order_by('-created_at')
    return render(request, 'municipality_portal/stalls/list.html', {'stalls': stalls})


@_admin_required
def stall_detail(request, pk):
    stall = get_object_or_404(Stall, pk=pk)
    return render(request, 'municipality_portal/stalls/detail.html', {'stall': stall})


@_admin_required
def stall_approve(request, pk):
    """Approve a pending stall application and assign a location."""
    stall = get_object_or_404(Stall, pk=pk, status=Stall.STATUS_PENDING)
    form = StallApprovalForm(request.POST or None, instance=stall)
    location_form = StallAssignLocationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid() and location_form.is_valid():
        stall = form.save(commit=False)
        stall.status = Stall.STATUS_ACTIVE
        stall.location = location_form.cleaned_data['location']
        stall.approved_by = request.user
        stall.approved_at = timezone.now()
        stall.save()
        # Notify vendor
        Notification.objects.create(
            recipient=stall.owner.user,
            notification_type=Notification.TYPE_APPROVAL,
            title='Your stall has been approved!',
            message=f'Your stall has been approved and assigned to {stall.location}.',
        )
        return redirect('municipality_portal:stall_list')

    return render(request, 'municipality_portal/stalls/approve.html', {
        'stall': stall,
        'form': form,
        'location_form': location_form,
    })


@_admin_required
def stall_reject(request, pk):
    stall = get_object_or_404(Stall, pk=pk, status=Stall.STATUS_PENDING)
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        stall.status = Stall.STATUS_REJECTED
        stall.rejection_reason = reason
        stall.save()
        Notification.objects.create(
            recipient=stall.owner.user,
            notification_type=Notification.TYPE_REJECTION,
            title='Your stall application was rejected.',
            message=reason,
        )
        return redirect('municipality_portal:stall_list')
    return render(request, 'municipality_portal/stalls/reject.html', {'stall': stall})


@_admin_required
def stall_suspend(request, pk):
    stall = get_object_or_404(Stall, pk=pk)
    if request.method == 'POST':
        stall.status = Stall.STATUS_SUSPENDED
        stall.save()
        return redirect('municipality_portal:stall_detail', pk=pk)
    return render(request, 'municipality_portal/stalls/suspend.html', {'stall': stall})


# ── Location Management ─────────────────────────────────────────────────────

@_admin_required
def location_list(request):
    locations = Location.objects.all().order_by('name')
    return render(request, 'municipality_portal/locations/list.html', {'locations': locations})


@_admin_required
def location_create(request):
    form = LocationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('municipality_portal:location_list')
    return render(request, 'municipality_portal/locations/form.html', {
        'form': form, 'title': 'Add Location'
    })


@_admin_required
def location_edit(request, pk):
    location = get_object_or_404(Location, pk=pk)
    form = LocationForm(request.POST or None, instance=location)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('municipality_portal:location_list')
    return render(request, 'municipality_portal/locations/form.html', {
        'form': form, 'title': 'Edit Location'
    })


# ── Vendor Management ───────────────────────────────────────────────────────

@_admin_required
def vendor_list(request):
    vendors = VendorProfile.objects.select_related('user').order_by('-created_at')
    return render(request, 'municipality_portal/vendors/list.html', {'vendors': vendors})


@_admin_required
def vendor_detail(request, pk):
    vendor = get_object_or_404(VendorProfile, pk=pk)
    return render(request, 'municipality_portal/vendors/detail.html', {'vendor': vendor})


# ── Officer Management ──────────────────────────────────────────────────────

@_admin_required
def officer_list(request):
    officers = OfficerProfile.objects.select_related('user').order_by('-created_at')
    return render(request, 'municipality_portal/officers/list.html', {'officers': officers})


@_admin_required
def officer_create(request):
    form = OfficerCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('municipality_portal:officer_list')
    return render(request, 'municipality_portal/officers/form.html', {
        'form': form, 'title': 'Add Officer'
    })


# ── Subscription Management ─────────────────────────────────────────────────

@_admin_required
def subscription_create(request, stall_pk):
    """Record a payment and create a new subscription for a stall."""
    stall = get_object_or_404(Stall, pk=stall_pk)
    form = SubscriptionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        sub = form.save(commit=False)
        sub.stall = stall
        sub.recorded_by = request.user
        sub.save()
        stall.status = Stall.STATUS_ACTIVE
        stall.save()
        return redirect('municipality_portal:stall_detail', pk=stall_pk)
    return render(request, 'municipality_portal/stalls/subscription_form.html', {
        'stall': stall, 'form': form
    })


# ── Violations ──────────────────────────────────────────────────────────────

@_admin_required
def violation_list(request):
    violations = Violation.objects.select_related(
        'stall__owner__user', 'officer'
    ).order_by('-created_at')
    return render(request, 'municipality_portal/violations/list.html', {
        'violations': violations
    })


# ── Reports ─────────────────────────────────────────────────────────────────

@_admin_required
def reports(request):
    context = {
        'inspections_by_result': Inspection.objects.values('result').order_by('result'),
        'violations_by_type': Violation.objects.values('violation_type').order_by('violation_type'),
        'active_subscriptions': Subscription.objects.filter(
            status=Subscription.STATUS_ACTIVE
        ).count(),
        'expiring_soon': Subscription.objects.filter(
            status=Subscription.STATUS_ACTIVE,
            expiry_date__lte=timezone.now().date()
        ).count(),
    }
    return render(request, 'municipality_portal/reports/index.html', context)
