from django.db import models

class BGBCamp(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active / Operational'),
        ('Inactive', 'Temporarily Inactive'),
    ]

    name = models.CharField(max_length=150)
    district = models.CharField(max_length=100, db_index=True)
    phone = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    operational_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"{self.name} BGB Camp - {self.district} ({self.operational_status})"
