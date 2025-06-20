import django_filters
from django import forms
from .models import CaregiverProfile, CaregiverCategory


class CaregiverFilter(django_filters.FilterSet):
    """Filter set for caregiver search"""
    
    categories = django_filters.ModelMultipleChoiceFilter(
        queryset=CaregiverCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    
    min_hourly_rate = django_filters.NumberFilter(
        field_name='hourly_rate',
        lookup_expr='gte'
    )
    
    max_hourly_rate = django_filters.NumberFilter(
        field_name='hourly_rate',
        lookup_expr='lte'
    )
    
    min_experience = django_filters.NumberFilter(
        field_name='years_of_experience',
        lookup_expr='gte'
    )
    
    min_rating = django_filters.NumberFilter(
        field_name='average_rating',
        lookup_expr='gte'
    )
    
    availability_status = django_filters.ChoiceFilter(
        choices=CaregiverProfile.AVAILABILITY_STATUS_CHOICES
    )
    
    skills = django_filters.CharFilter(
        method='filter_skills'
    )
    
    languages = django_filters.CharFilter(
        method='filter_languages'
    )
    
    age_groups = django_filters.CharFilter(
        method='filter_age_groups'
    )
    
    special_needs = django_filters.BooleanFilter(
        field_name='special_needs_experience'
    )
    
    working_days = django_filters.CharFilter(
        method='filter_working_days'
    )
    
    class Meta:
        model = CaregiverProfile
        fields = []
    
    def filter_skills(self, queryset, name, value):
        """Filter by skills (case-insensitive partial match)"""
        if value:
            return queryset.filter(skills__icontains=value)
        return queryset
    
    def filter_languages(self, queryset, name, value):
        """Filter by languages (case-insensitive partial match)"""
        if value:
            return queryset.filter(languages__icontains=value)
        return queryset
    
    def filter_age_groups(self, queryset, name, value):
        """Filter by age groups (case-insensitive partial match)"""
        if value:
            return queryset.filter(age_groups__icontains=value)
        return queryset
    
    def filter_working_days(self, queryset, name, value):
        """Filter by working days (case-insensitive partial match)"""
        if value:
            return queryset.filter(working_days__icontains=value)
        return queryset