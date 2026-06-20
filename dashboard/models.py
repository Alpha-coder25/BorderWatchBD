from django.db import models
from django.contrib.auth.models import User
from reports.models import Report

class VerificationLog(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='verification_logs')
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='moderation_logs')
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Log #{self.id}: Report #{self.report.id} status changed from {self.previous_status} to {self.new_status}"
