from django import forms

from apps.stalls.models import Stall, StallImage


class StallApplicationForm(forms.ModelForm):
    class Meta:
        model = Stall
        fields = ['category', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class StallImageForm(forms.ModelForm):
    class Meta:
        model = StallImage
        fields = ['image', 'caption']
