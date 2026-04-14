from django.contrib import admin

from .models import Location, LocationCategory, Reservation


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'max_stalls', 'is_active')
    list_filter = ('is_active',)


@admin.register(LocationCategory)
class LocationCategoryAdmin(admin.ModelAdmin):
    list_display = ('location', 'category')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'location', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status',)
    raw_id_fields = ('vendor', 'location')
