from django import forms
from django.contrib.auth.forms import UserCreationForm

from apps.accounts.models import CustomUser, OfficerProfile
from apps.locations.models import Location
from apps.stalls.models import Stall
from apps.subscriptions.models import Subscription


class StallApprovalForm(forms.ModelForm):
    class Meta:
        model = Stall
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class StallAssignLocationForm(forms.Form):
    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True),
        empty_label="Select a location",
    )


DAYS_CHOICES = [
    ('monday', 'الإثنين'),
    ('tuesday', 'الثلاثاء'),
    ('wednesday', 'الأربعاء'),
    ('thursday', 'الخميس'),
    ('friday', 'الجمعة'),
    ('saturday', 'السبت'),
    ('sunday', 'الأحد'),
]

class LocationForm(forms.ModelForm):
    allowed_days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="أيام العمل المسموحة",
        required=True
    )

    class Meta:
        model = Location
        fields = [
            'name', 'latitude', 'longitude', 'radius_meters',
            'allowed_days', 'start_time', 'end_time', 'max_stalls',
            'is_active', 'notes',
        ]
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class OfficerCreationForm(UserCreationForm):
    """Creates a CustomUser (role=officer) + OfficerProfile in one step."""
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone = forms.CharField(max_length=20, required=False)
    badge_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.ROLE_OFFICER
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
            OfficerProfile.objects.create(
                user=user,
                badge_number=self.cleaned_data['badge_number'],
            )
        return user


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['plan_type', 'amount', 'start_date', 'expiry_date', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
