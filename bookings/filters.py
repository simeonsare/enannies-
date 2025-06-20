import django_filters
from django import forms
from .models import Booking


class BookingFilter(django_filters.FilterSet):
    """Filter set for booking search"""
    
    status = django_filters.MultipleChoiceFilter(
        choices=Booking.STATUS_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )
    
    start_date = django_filters.DateFilter(
        field_name='start_datetime',
        lookup_expr='date__gte',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    end_date = django_filters.DateFilter(
        field_name='start_datetime',
        lookup_expr='date__lte',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    min_amount = django_filters.NumberFilter(
        field_name='total_amount',
        lookup_expr='gte'
    )
    
    max_amount = django_filters.NumberFilter(
        field_name='total_amount',
        lookup_expr='lte'
    )
    
    caregiver = django_filters.CharFilter(
        field_name='caregiver__user__first_name',
        lookup_expr='icontains'
    )
    
    customer = django_filters.CharFilter(
        field_name='customer__first_name',
        lookup_expr='icontains'
    )
    
    service_city = django_filters.CharFilter(
        field_name='service_city',
        lookup_expr='icontains'
    )
    
    payment_status = django_filters.ChoiceFilter(
        choices=[
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('refunded', 'Refunded'),
            ('failed', 'Failed'),
        ]
    )
    
    class Meta:
        model = Booking
        fields = []