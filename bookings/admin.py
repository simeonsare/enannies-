from django.contrib import admin
from .models import BookingRequest, BookingMessage

@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'caregiver', 'service_type', 'start_date', 'status', 'total_amount']
    list_filter = ['status', 'service_type', 'start_date', 'created_at']
    search_fields = ['customer__first_name', 'customer__last_name', 'caregiver__first_name', 'caregiver__last_name']
    readonly_fields = ['created_at', 'updated_at', 'total_amount']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'caregiver', 'service_type', 'status')
        }),
        ('Service Details', {
            'fields': ('number_of_children', 'children_ages', 'special_instructions', 'service_address')
        }),
        ('Scheduling', {
            'fields': ('start_date', 'start_time', 'end_time', 'duration_hours')
        }),
        ('Pricing', {
            'fields': ('hourly_rate', 'total_amount')
        }),
        ('Response', {
            'fields': ('caregiver_response_message', 'responded_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(BookingMessage)
class BookingMessageAdmin(admin.ModelAdmin):
    list_display = ['booking', 'sender', 'message', 'created_at']
    list_filter = ['created_at']
    search_fields = ['booking__id', 'sender__first_name', 'sender__last_name', 'message']
    readonly_fields = ['created_at']