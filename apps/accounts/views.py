from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, VendorRegistrationForm
from .models import CustomUser, OfficerProfile


def login_view(request):
    """Unified login. Redirects to the correct portal based on role after login."""
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    form = LoginForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return _redirect_by_role(user)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def register_vendor(request):
    """
    Public registration for new vendors.
    Creates a CustomUser (role=vendor) + VendorProfile (status=pending).
    Admin must approve before the vendor can operate.
    """
    if request.user.is_authenticated:
        return _redirect_by_role(request.user)

    form = VendorRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('vendor_portal:dashboard')

    return render(request, 'accounts/register_vendor.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


def demo_login(request, role):
    """
    Prototype demo: instantly log in as a pre-built mock user for any role.
    Creates the user on first access if it doesn't exist yet.
    """
    DEMO_USERS = {
        CustomUser.ROLE_CITIZEN: {
            'username': 'demo_citizen',
            'first_name': 'سارة',
            'last_name': 'إبراهيم',
        },
        CustomUser.ROLE_VENDOR: {
            'username': 'demo_vendor',
            'first_name': 'محمد',
            'last_name': 'الشريف',
        },
        CustomUser.ROLE_OFFICER: {
            'username': 'demo_officer',
            'first_name': 'أحمد',
            'last_name': 'الخطيب',
        },
        CustomUser.ROLE_ADMIN: {
            'username': 'demo_admin',
            'first_name': 'خالد',
            'last_name': 'العمر',
        },
    }

    if role not in DEMO_USERS:
        return redirect('public_portal:map')

    info = DEMO_USERS[role]
    user, created = CustomUser.objects.get_or_create(
        username=info['username'],
        defaults={
            'role': role,
            'first_name': info['first_name'],
            'last_name': info['last_name'],
        },
    )
    if created:
        user.set_unusable_password()
        user.save()
    elif user.role != role:
        user.role = role
        user.save(update_fields=['role'])

    if role == CustomUser.ROLE_OFFICER:
        OfficerProfile.objects.get_or_create(
            user=user,
            defaults={'badge_number': 'OFC-001'},
        )
    elif role == CustomUser.ROLE_VENDOR:
        from apps.accounts.models import VendorProfile
        VendorProfile.objects.get_or_create(
            user=user,
            defaults={'national_id': '999999999'},
        )

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return _redirect_by_role(user)


def _redirect_by_role(user):
    role_redirect = {
        CustomUser.ROLE_CITIZEN: 'public_portal:map',
        CustomUser.ROLE_VENDOR: 'vendor_portal:dashboard',
        CustomUser.ROLE_OFFICER: 'officer_portal:dashboard',
        CustomUser.ROLE_ADMIN: 'municipality_portal:dashboard',
    }
    url_name = role_redirect.get(user.role, 'public_portal:map')
    return redirect(url_name)
