import uuid
from django.conf import settings
from django.db import models


class StallCategory(models.Model):
    """
    Type of goods/activity the stall sells (e.g. Food, Clothing, Electronics).
    Used to enforce location-activity conflict rules.
    """
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class or emoji")

    def __str__(self):
        return self.name


class Stall(models.Model):
    """
    Core entity. Represents a single regulated street stall.
    Lifecycle: pending → active → expired/suspended
    """
    STATUS_PENDING = 'pending'
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_SUSPENDED = 'suspended'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Approval'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_SUSPENDED, 'Suspended'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    owner = models.ForeignKey(
        'accounts.VendorProfile', on_delete=models.CASCADE, related_name='stalls'
    )
    location = models.ForeignKey(
        'locations.Location', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='stalls'
    )
    category = models.ForeignKey(
        StallCategory, on_delete=models.PROTECT, related_name='stalls'
    )
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # QR system: unique token embedded in the QR code URL
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    qr_code_image = models.ImageField(
        upload_to='qr_codes/', null=True, blank=True
    )

    rejection_reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='approved_stalls'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_qr_verify_url(self):
        from django.urls import reverse
        return reverse('public_portal:verify_qr', kwargs={'token': str(self.qr_token)})

    def is_open_now(self):
        if self.status != self.STATUS_ACTIVE:
            return False
        if self.location:
            return self.location.is_currently_open()
        return False

    def __str__(self):
        return f"Stall #{self.pk} — {self.owner.user.get_full_name()} [{self.get_status_display()}]"


class StallImage(models.Model):
    """
    Up to 5 images per stall showing actual products (business rule).
    """
    stall = models.ForeignKey(Stall, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='stall_images/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.stall}"
