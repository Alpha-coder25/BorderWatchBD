from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import AnonymousToken

class ReportCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Report Categories"

    def __str__(self):
        return self.name

class Report(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending Review'),
        ('Verified', 'Verified (Public)'),
        ('Rejected', 'Rejected'),
        ('Escalated', 'Escalated to Authorities'),
    ]

    SEVERITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    ]

    # Links
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    anonymous_token = models.ForeignKey(AnonymousToken, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    
    # Details
    incident_type = models.ForeignKey(ReportCategory, on_delete=models.PROTECT, related_name='reports', db_index=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Geo-Coordinates with db index
    latitude = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, db_index=True)
    
    # Priority & Severity
    severity = models.CharField(max_length=15, choices=SEVERITY_CHOICES, default='Medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending', db_index=True)
    
    # Scores
    urgency = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])  # Urgency score 1-5
    credibility = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])  # Credibility score 1-5
    priority_score = models.IntegerField(default=9)  # Priority = Severity Weight * Urgency * Credibility
    is_priority = models.BooleanField(default=False)
    is_possible_duplicate = models.BooleanField(default=False)
    is_displayed = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def calculate_priority(self):
        # Severity weights: Low = 1, Medium = 2, High = 3, Critical = 5
        severity_weights = {
            'Low': 1,
            'Medium': 2,
            'High': 3,
            'Critical': 5
        }
        weight = severity_weights.get(self.severity, 2)
        
        # Calculate credibility based on reporter type if not manually set
        if self.user:
            try:
                if self.user.profile.is_verified:
                    self.credibility = 5
                else:
                    self.credibility = 4
            except Exception:
                self.credibility = 4
        else:
            # Anonymous submissions start with lower credibility
            self.credibility = 2

        self.priority_score = weight * self.urgency * self.credibility
        
        # Critical severity reports or high priority score gets flagged as is_priority
        if self.severity == 'Critical' or self.priority_score >= 30:
            self.is_priority = True
        else:
            self.is_priority = False

    def save(self, *args, **kwargs):
        self.calculate_priority()
        super().save(*args, **kwargs)

    def __str__(self):
        reporter = self.user.username if self.user else "Anonymous"
        return f"Report #{self.id}: {self.title} ({self.status}) - by {reporter}"

class ReportEvidence(models.Model):
    FILE_TYPE_CHOICES = [
        ('image', 'Image File'),
        ('video', 'Video File'),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='evidence')
    file = models.FileField(upload_to='reports/evidence/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidence for Report #{self.report.id} ({self.get_file_type_display()})"
