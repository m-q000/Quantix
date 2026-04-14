from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, VendorRegistrationForm
from .models import CustomUser


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


def _redirect_by_role(user):
    role_redirect = {
        CustomUser.ROLE_CITIZEN: 'public_portal:map',
        CustomUser.ROLE_VENDOR: 'vendor_portal:dashboard',
        CustomUser.ROLE_OFFICER: 'officer_portal:dashboard',
        CustomUser.ROLE_ADMIN: 'municipality_portal:dashboard',
    }
    url_name = role_redirect.get(user.role, 'public_portal:map')
    return redirect(url_name)
