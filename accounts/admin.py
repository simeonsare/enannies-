from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CustomerProfile, CaregiverProfile

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['email', 'username', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_active']
    list_filter = ['user_type', 'is_verified', 'is_active', 'date_joined']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_type', 'phone_number', 'is_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('email', 'user_type', 'phone_number')}),
    )
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['email']

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'number_of_children', 'address']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    list_filter = ['number_of_children']

@admin.register(CaregiverProfile)
class CaregiverProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'years_of_experience', 'hourly_rate', 'location', 'available', 'rating']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'location']
    list_filter = ['years_of_experience', 'available', 'rating']
    readonly_fields = ['rating', 'total_reviews']

admin.site.register(User, CustomUserAdmin)