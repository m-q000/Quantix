from django import forms

from apps.locations.models import Location, Reservation
from apps.stalls.models import Stall, StallImage


class ReservationForm(forms.ModelForm):
    """Vendor reserves a municipality-defined location for a date range."""

    class Meta:
        model = Reservation
        fields = ['location', 'start_date', 'end_date', 'notes']
        widgets = {
            'location': forms.HiddenInput(attrs={'id': 'id_location_selected'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control',
                                           'placeholder': 'ملاحظات إضافية (اختياري)...'}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError('تاريخ الانتهاء يجب أن يكون بعد تاريخ البداية')
        return cleaned


class StallApplicationForm(forms.ModelForm):
    """
    Vendor submits a stall application.
    Location is chosen via the interactive map (hidden input).
    """

    class Meta:
        model = Stall
        fields = ['location', 'category', 'description']
        widgets = {
            # Controlled by the Leaflet map in apply.html
            'location': forms.HiddenInput(attrs={'id': 'id_location_selected'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only offer active locations and allow blank (vendor may leave unset)
        self.fields['location'].queryset = Location.objects.filter(is_active=True)
        self.fields['location'].required = False


class StallImageForm(forms.ModelForm):
    class Meta:
        model = StallImage
        fields = ['image', 'caption']
