from django import forms

from apps.locations.models import Location
from apps.stalls.models import Stall, StallImage


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
