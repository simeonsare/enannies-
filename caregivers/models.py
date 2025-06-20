from django.db import models
from accounts.models import User

class CaregiverService(models.Model):
    SERVICE_TYPES = (
        ('babysitting', 'Babysitting'),
        ('nanny', 'Nanny Services'),
        ('tutoring', 'Tutoring'),
        ('special_needs', 'Special Needs Care'),
        ('overnight', 'Overnight Care'),
    )
    
    caregiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.TextField()
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2)
    age_range_min = models.PositiveIntegerField(default=0)
    age_range_max = models.PositiveIntegerField(default=18)
    
    def __str__(self):
        return f"{self.caregiver.get_full_name()} - {self.get_service_type_display()}"

class CaregiverAvailability(models.Model):
    DAYS_OF_WEEK = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )
    
    caregiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['caregiver', 'day_of_week']
    
    def __str__(self):
        return f"{self.caregiver.get_full_name()} - {self.get_day_of_week_display()}"

class Review(models.Model):
    caregiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['caregiver', 'customer']
    
    def __str__(self):
        return f"Review for {self.caregiver.get_full_name()} by {self.customer.get_full_name()}"