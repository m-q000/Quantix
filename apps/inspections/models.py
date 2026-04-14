from django.conf import settings
from django.db import models


class Inspection(models.Model):
    """
    Record of a single QR scan + validation by an officer.
    The four boolean flags map to the four business rules checked at scan time.
    """
    RESULT_OK = 'ok'
    RESULT_WARNING = 'warning'
    RESULT_VIOLATION = 'violation'

    RESULT_CHOICES = [
        (RESULT_OK, 'OK'),
        (RESULT_WARNING, 'Warning'),
        (RESULT_VIOLATION, 'Violation'),
    ]

    stall = models.ForeignKey(
        'stalls.Stall', on_delete=models.CASCADE, related_name='inspections'
    )
    officer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inspections'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)

    # Validation flags set automatically at scan time
    valid_location = models.BooleanField(default=False)
    valid_time = models.BooleanField(default=False)
    valid_activity = models.BooleanField(default=False)
    valid_subscription = models.BooleanField(default=False)

    # Officer GPS coordinates at scan time
    officer_latitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    officer_longitude = models.DecimalField(
        max_digits=10, decimal_places=7, null=True, blank=True
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Inspection #{self.pk} — {self.stall} [{self.get_result_display()}]"


class Violation(models.Model):
    """
    Formal violation record. Linked to an inspection.
    Repeated violations trigger suspension (enforced via admin or automated rule).
    """
    TYPE_OUT_OF_LOCATION = 'out_of_location'
    TYPE_OUT_OF_TIME = 'out_of_time'
    TYPE_WRONG_ACTIVITY = 'wrong_activity'
    TYPE_NO_QR = 'no_qr'
    TYPE_EXPIRED_SUBSCRIPTION = 'expired_subscription'

    TYPE_CHOICES = [
        (TYPE_OUT_OF_LOCATION, 'Out of Location'),
        (TYPE_OUT_OF_TIME, 'Out of Time'),
        (TYPE_WRONG_ACTIVITY, 'Wrong Activity'),
        (TYPE_NO_QR, 'No QR Code'),
        (TYPE_EXPIRED_SUBSCRIPTION, 'Expired Subscription'),
    ]

    ACTION_WARNING = 'warning'
    ACTION_FINE = 'fine'
    ACTION_SUSPENSION = 'suspension'

    ACTION_CHOICES = [
        (ACTION_WARNING, 'Warning'),
        (ACTION_FINE, 'Fine'),
        (ACTION_SUSPENSION, 'Suspension'),
    ]

    inspection = models.ForeignKey(
        Inspection, on_delete=models.CASCADE, related_name='violations'
    )
    stall = models.ForeignKey(
        'stalls.Stall', on_delete=models.CASCADE, related_name='violations'
    )
    officer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='issued_violations'
    )
    violation_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    evidence_image = models.ImageField(
        upload_to='violation_images/', null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Violation #{self.pk} — {self.get_violation_type_display()} "
            f"on {self.stall} [{self.get_action_display()}]"
        )
