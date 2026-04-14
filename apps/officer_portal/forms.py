from django import forms

from apps.inspections.models import Inspection, Violation


class InspectionForm(forms.ModelForm):
    class Meta:
        model = Inspection
        fields = ['result', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class ViolationForm(forms.ModelForm):
    class Meta:
        model = Violation
        fields = ['violation_type', 'action', 'description', 'evidence_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
