from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Central user model. role determines which portal the user accesses.
    """
    ROLE_CITIZEN = 'citizen'
    ROLE_VENDOR = 'vendor'
    ROLE_OFFICER = 'officer'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_CITIZEN, 'Citizen'),
        (ROLE_VENDOR, 'Vendor'),
        (ROLE_OFFICER, 'Officer'),
        (ROLE_ADMIN, 'Municipality Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CITIZEN)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_citizen(self):
        return self.role == self.ROLE_CITIZEN

    def is_vendor(self):
        return self.role == self.ROLE_VENDOR

    def is_officer(self):
        return self.role == self.ROLE_OFFICER

    def is_municipality_admin(self):
        return self.role == self.ROLE_ADMIN

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class VendorProfile(models.Model):
    """
    Extended profile for users with role=vendor.
    Created on vendor registration; status managed by municipality admin.
    """
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_SUSPENDED = 'suspended'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_SUSPENDED, 'Suspended'),
    ]

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='vendor_profile'
    )
    national_id = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    rejection_reason = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vendor: {self.user.get_full_name()} [{self.get_status_display()}]"


class OfficerProfile(models.Model):
    """
    Extended profile for users with role=officer.
    Created directly by municipality admins.
    """
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='officer_profile'
    )
    badge_number = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Officer: {self.user.get_full_name()} (Badge: {self.badge_number})"
