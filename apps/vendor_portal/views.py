from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.stalls.models import Stall, StallImage
from apps.subscriptions.models import Subscription
from apps.inspections.models import Violation

from .forms import StallApplicationForm, StallImageForm


def _vendor_required(view_func):
    """Decorator: user must be authenticated and have role=vendor."""
    from functools import wraps
    from apps.accounts.models import CustomUser

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != CustomUser.ROLE_VENDOR:
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@_vendor_required
def dashboard(request):
    """Vendor home: summary of stall status, subscription, recent violations."""
    vendor = request.user.vendor_profile
    stall = Stall.objects.filter(owner=vendor).first()
    active_subscription = None
    if stall:
        active_subscription = (
            Subscription.objects.filter(stall=stall, status=Subscription.STATUS_ACTIVE)
            .order_by('-expiry_date')
            .first()
        )
    return render(request, 'vendor_portal/dashboard.html', {
        'vendor': vendor,
        'stall': stall,
        'subscription': active_subscription,
    })


@_vendor_required
def apply_stall(request):
    """Submit a new stall application (only if no existing stall)."""
    vendor = request.user.vendor_profile
    if Stall.objects.filter(owner=vendor).exists():
        return redirect('vendor_portal:my_stall')

    form = StallApplicationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        stall = form.save(commit=False)
        stall.owner = vendor
        stall.status = Stall.STATUS_PENDING
        stall.save()
        return redirect('vendor_portal:my_stall')

    return render(request, 'vendor_portal/apply.html', {'form': form})


@_vendor_required
def my_stall(request):
    """Vendor's stall detail: status, location, schedule, images."""
    vendor = request.user.vendor_profile
    stall = get_object_or_404(Stall, owner=vendor)
    return render(request, 'vendor_portal/my_stall.html', {'stall': stall})


@_vendor_required
def upload_images(request):
    """Upload stall images (max 5 per business rule)."""
    vendor = request.user.vendor_profile
    stall = get_object_or_404(Stall, owner=vendor)

    MAX_IMAGES = 5
    image_count = stall.images.count()

    form = StallImageForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        if image_count < MAX_IMAGES:
            img = form.save(commit=False)
            img.stall = stall
            img.save()
        return redirect('vendor_portal:my_stall')

    return render(request, 'vendor_portal/upload_images.html', {
        'stall': stall,
        'form': form,
        'image_count': image_count,
        'max_images': MAX_IMAGES,
    })


@_vendor_required
def qr_code(request):
    """Download QR code for the vendor's stall."""
    vendor = request.user.vendor_profile
    stall = get_object_or_404(Stall, owner=vendor)
    return render(request, 'vendor_portal/qr_code.html', {'stall': stall})


@_vendor_required
def subscription(request):
    """View subscription history and renewal status."""
    vendor = request.user.vendor_profile
    stall = get_object_or_404(Stall, owner=vendor)
    subscriptions = Subscription.objects.filter(stall=stall).order_by('-expiry_date')
    return render(request, 'vendor_portal/subscription.html', {
        'stall': stall,
        'subscriptions': subscriptions,
    })


@_vendor_required
def violations(request):
    """View all violations issued against the vendor's stall."""
    vendor = request.user.vendor_profile
    stall = get_object_or_404(Stall, owner=vendor)
    all_violations = Violation.objects.filter(stall=stall).order_by('-created_at')
    return render(request, 'vendor_portal/violations.html', {
        'stall': stall,
        'violations': all_violations,
    })
