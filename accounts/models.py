import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    ROLE_CHOICES = [
        ('resident', 'Border Resident'),
        ('farmer', 'Farmer'),
        ('traveler', 'Traveler'),
        ('tourist', 'Tourist'),
        ('transport_worker', 'Local Transport Worker'),
        ('witness', 'Civilian Witness'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    phone = models.CharField(max_length=15, blank=True, null=True)
    nid = models.CharField(max_length=20, blank=True, null=True, verbose_name="National ID (NID)")
    district = models.CharField(max_length=50, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.get_role_display()})"

class AnonymousToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token is valid for 24 hours by default
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_active(self):
        return not self.is_used and not self.is_expired

    def __str__(self):
        return f"Token: {self.token} (Used: {self.is_used}, Active: {self.is_active})"
