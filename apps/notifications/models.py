from django.conf import settings
from django.db import models


class Notification(models.Model):
    """
    In-app notification delivered to any user role.
    Types cover all business events: approvals, rejections, expiry warnings, violations.
    """
    TYPE_APPROVAL = 'approval'
    TYPE_REJECTION = 'rejection'
    TYPE_EXPIRY_WARNING = 'expiry_warning'
    TYPE_VIOLATION = 'violation'
    TYPE_NEW_APPLICATION = 'new_application'
    TYPE_NEW_REPORT = 'new_report'
    TYPE_GENERAL = 'general'

    TYPE_CHOICES = [
        (TYPE_APPROVAL, 'Stall Approved'),
        (TYPE_REJECTION, 'Stall Rejected'),
        (TYPE_EXPIRY_WARNING, 'Subscription Expiring Soon'),
        (TYPE_VIOLATION, 'Violation Issued'),
        (TYPE_NEW_APPLICATION, 'New Application (Admin)'),
        (TYPE_NEW_REPORT, 'New Citizen Report (Admin)'),
        (TYPE_GENERAL, 'General'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    # Optional deep-link URL to the relevant object
    link = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_notification_type_display()}] → {self.recipient.username}"
