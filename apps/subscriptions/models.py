from django.conf import settings
from django.db import models


class Subscription(models.Model):
    """
    Active subscription is required for a stall to be considered valid during inspection.
    Expiry automatically marks the stall as expired (via management command / celery task).
    """
    PLAN_DAILY = 'daily'
    PLAN_MONTHLY = 'monthly'
    PLAN_SEASONAL = 'seasonal'

    PLAN_CHOICES = [
        (PLAN_DAILY, 'Daily'),
        (PLAN_MONTHLY, 'Monthly'),
        (PLAN_SEASONAL, 'Seasonal'),
    ]

    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    stall = models.ForeignKey(
        'stalls.Stall', on_delete=models.CASCADE, related_name='subscriptions'
    )
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='recorded_subscriptions',
        help_text="Municipality admin who recorded the payment"
    )
    paid_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def is_valid(self):
        from django.utils import timezone
        return self.status == self.STATUS_ACTIVE and self.expiry_date >= timezone.now().date()

    def __str__(self):
        return f"{self.stall} — {self.get_plan_type_display()} (expires {self.expiry_date})"


class SubscriptionRenewalAlert(models.Model):
    """
    Tracks renewal alert notifications so they are sent only once per expiry cycle.
    """
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name='renewal_alerts'
    )
    alert_sent_at = models.DateTimeField(auto_now_add=True)
    days_before_expiry = models.IntegerField()

    def __str__(self):
        return f"Alert for {self.subscription} ({self.days_before_expiry}d before expiry)"
