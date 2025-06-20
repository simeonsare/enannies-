from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    USER_TYPES = (
        ('customer', 'Customer'),
        ('caregiver', 'Caregiver'),
        ('admin', 'Admin'),
    )
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.user_type})"

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=17, blank=True)
    number_of_children = models.PositiveIntegerField(default=1)
    children_ages = models.CharField(max_length=100, blank=True, help_text="Comma-separated ages")
    special_needs = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/customers/', blank=True, null=True)
    
    def __str__(self):
        return f"Customer: {self.user.get_full_name()}"

class CaregiverProfile(models.Model):
    EXPERIENCE_CHOICES = (
        ('0-1', '0-1 years'),
        ('1-3', '1-3 years'),
        ('3-5', '3-5 years'),
        ('5-10', '5-10 years'),
        ('10+', '10+ years'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='caregiver_profile')
    bio = models.TextField(max_length=500, blank=True)
    years_of_experience = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES, default='0-1')
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    location = models.CharField(max_length=100, blank=True)
    available = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='profiles/caregivers/', blank=True, null=True)
    certifications = models.TextField(blank=True, help_text="List any relevant certifications")
    languages = models.CharField(max_length=200, blank=True, help_text="Languages spoken")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"Caregiver: {self.user.get_full_name()}"