from django.contrib import admin
from .models import CaregiverService, CaregiverAvailability, Review

@admin.register(CaregiverService)
class CaregiverServiceAdmin(admin.ModelAdmin):
    list_display = ['caregiver', 'service_type', 'price_per_hour', 'age_range_min', 'age_range_max']
    list_filter = ['service_type', 'price_per_hour']
    search_fields = ['caregiver__first_name', 'caregiver__last_name', 'caregiver__email']

@admin.register(CaregiverAvailability)
class CaregiverAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['caregiver', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']
    search_fields = ['caregiver__first_name', 'caregiver__last_name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['caregiver', 'customer', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['caregiver__first_name', 'caregiver__last_name', 'customer__first_name', 'customer__last_name']
    readonly_fields = ['created_at']