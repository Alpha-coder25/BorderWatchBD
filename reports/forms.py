from django import forms
from .models import Report, ReportCategory
from .validators import validate_evidence_file
from accounts.models import AnonymousToken

class ReportForm(forms.ModelForm):
    # Form fields for evidence files
    evidence_1 = forms.FileField(required=False, validators=[validate_evidence_file], label="Evidence Attachment 1 (Image/Video)")
    evidence_2 = forms.FileField(required=False, validators=[validate_evidence_file], label="Evidence Attachment 2 (Image/Video)")
    
    # Text field for entering anonymous token
    token_str = forms.CharField(
        required=False, 
        label="Anonymous Reporting Token",
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your 24h token if reporting anonymously...',
            'class': 'form-control'
        }),
        help_text="Required only if you are not logged in and wish to submit anonymously."
    )

    class Meta:
        model = Report
        fields = ['incident_type', 'title', 'description', 'latitude', 'longitude', 'severity', 'urgency']
        widgets = {
            'incident_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Provide a brief, clear title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe what happened in detail...'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'id': 'id_latitude'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'id': 'id_longitude'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'urgency': forms.Select(choices=[(i, str(i)) for i in range(1, 6)], attrs={'class': 'form-select'}),
        }

    def clean_urgency(self):
        urgency = self.cleaned_data.get('urgency')
        if not (1 <= int(urgency) <= 5):
            raise forms.ValidationError("Urgency must be between 1 and 5.")
        return urgency

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('latitude')
        lon = cleaned_data.get('longitude')

        # Geolocation bounds check (Bangladesh approx limits)
        if lat and not (20.0 <= float(lat) <= 27.0):
            self.add_error('latitude', "Latitude must be within Bangladesh boundaries (20.0 to 27.0).")
        if lon and not (88.0 <= float(lon) <= 93.0):
            self.add_error('longitude', "Longitude must be within Bangladesh boundaries (88.0 to 93.0).")

        return cleaned_data
