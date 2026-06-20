from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True, label="Identify as")
    phone = forms.CharField(max_length=15, required=False, help_text="Optional, for contact verification.")
    nid = forms.CharField(max_length=20, required=False, label="National ID (NID)", help_text="Optional, verified profiles have high priority.")
    district = forms.CharField(max_length=50, required=False, help_text="Optional, local district of residence.")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.create(
                user=user,
                role=self.cleaned_data.get('role'),
                phone=self.cleaned_data.get('phone'),
                nid=self.cleaned_data.get('nid'),
                district=self.cleaned_data.get('district')
            )
        return user

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ['role', 'phone', 'nid', 'district']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.user.email = self.cleaned_data.get('email')
            profile.user.save()
            profile.save()
        return profile
