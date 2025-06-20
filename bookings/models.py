from django.db import models
from django.utils import timezone
from accounts.models import User
from caregivers.models import CaregiverService

class BookingRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    SERVICE_TYPES = (
        ('babysitting', 'Babysitting'),
        ('nanny', 'Nanny Services'),
        ('tutoring', 'Tutoring'), 
        ('special_needs', 'Special Needs Care'),
        ('overnight', 'Overnight Care'),
    )
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    caregiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caregiver_bookings')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    
    # Service specifications
    number_of_children = models.PositiveIntegerField(default=1)
    children_ages = models.CharField(max_length=100, help_text="Comma-separated ages (e.g., 3, 5, 8)")
    special_instructions = models.TextField(blank=True)
    
    # Scheduling
    start_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=4, decimal_places=2)
    
    # Location
    service_address = models.TextField()
    
    # Pricing
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Response from caregiver
    caregiver_response_message = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking #{self.id} - {self.customer.get_full_name()} to {self.caregiver.get_full_name()}"
    
    @property
    def is_upcoming(self):
        return self.start_date >= timezone.now().date() and self.status == 'accepted'
    
    @property
    def can_be_cancelled(self):
        return self.status in ['pending', 'accepted'] and self.start_date > timezone.now().date()

class BookingMessage(models.Model):
    booking = models.ForeignKey(BookingRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.get_full_name()} in Booking #{self.booking.id}"