from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser, VendorProfile


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class VendorRegistrationForm(UserCreationForm):
    """
    Creates CustomUser (role=vendor) + VendorProfile in one step.
    """
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone = forms.CharField(max_length=20, required=True)
    national_id = forms.CharField(max_length=20, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.ROLE_VENDOR
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
            VendorProfile.objects.create(
                user=user,
                national_id=self.cleaned_data['national_id'],
            )
        return user
