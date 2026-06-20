from django.db import models

class Alert(models.Model):
    ALERT_TYPES = [
        ('missing_person', 'Missing Person Alert'),
        ('danger_warning', 'High-Risk Warning'),
        ('general_alert', 'Border General Notice'),
    ]

    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=ALERT_TYPES, default='general_alert')
    priority = models.CharField(max_length=15, choices=PRIORITY_CHOICES, default='Medium')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} - {self.title} ({self.priority})"
