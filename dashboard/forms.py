from django import forms
from django.contrib.auth.models import User
from accounts.models import Profile


class AdminUserEditForm(forms.ModelForm):
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=False, label='User Role')
    phone = forms.CharField(required=False, max_length=15, label='Phone Number')
    nid = forms.CharField(required=False, max_length=20, label='National ID (NID)')
    district = forms.CharField(required=False, max_length=50, label='District')
    is_verified = forms.BooleanField(required=False, label='Verified Reporter')

    class Meta:
        model = User
        fields = ['username', 'email', 'is_active']

    def __init__(self, *args, profile_instance=None, **kwargs):
        self.profile_instance = profile_instance
        if self.profile_instance:
            initial = kwargs.get('initial', {})
            initial.update({
                'role': self.profile_instance.role,
                'phone': self.profile_instance.phone,
                'nid': self.profile_instance.nid,
                'district': self.profile_instance.district,
                'is_verified': self.profile_instance.is_verified,
            })
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super().save(commit=commit)
        if not self.profile_instance:
            self.profile_instance = Profile.objects.create(user=user)

        self.profile_instance.role = self.cleaned_data.get('role') or self.profile_instance.role
        self.profile_instance.phone = self.cleaned_data.get('phone')
        self.profile_instance.nid = self.cleaned_data.get('nid')
        self.profile_instance.district = self.cleaned_data.get('district')
        self.profile_instance.is_verified = self.cleaned_data.get('is_verified', False)

        if commit:
            self.profile_instance.save()
        return user
