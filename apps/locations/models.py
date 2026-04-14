from django.db import models


class Location(models.Model):
    """
    A predefined physical spot on the street where a stall can be placed.
    The municipality defines these zones including allowed categories and schedule.
    """
    name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    # GPS tolerance radius in meters (business rule: 10–20 m)
    radius_meters = models.IntegerField(default=15)
    # JSON list of allowed day names: ["monday", "tuesday", ...]
    allowed_days = models.JSONField(default=list)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_stalls = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def is_currently_open(self):
        from django.utils import timezone
        import datetime
        now = timezone.localtime()
        day_name = now.strftime('%A').lower()
        current_time = now.time()
        return (
            day_name in self.allowed_days
            and self.start_time <= current_time <= self.end_time
        )


class LocationCategory(models.Model):
    """
    Links a Location to a StallCategory it allows.
    Enforces activity conflict prevention with nearby shops.
    """
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name='allowed_categories'
    )
    category = models.ForeignKey(
        'stalls.StallCategory', on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('location', 'category')

    def __str__(self):
        return f"{self.location.name} → {self.category.name}"
