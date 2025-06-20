from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Avg
from accounts.models import User
from .models import CaregiverService, CaregiverAvailability, Review
from .serializers import (
    CaregiverServiceSerializer, CaregiverAvailabilitySerializer, 
    ReviewSerializer, CaregiverListSerializer
)

class CaregiverListAPIView(generics.ListAPIView):
    serializer_class = CaregiverListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = User.objects.filter(user_type='caregiver', is_active=True)
        
        # Filter parameters
        search = self.request.query_params.get('search', None)
        location = self.request.query_params.get('location', None)
        service_type = self.request.query_params.get('service_type', None)
        min_rate = self.request.query_params.get('min_rate', None)
        max_rate = self.request.query_params.get('max_rate', None)
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(caregiver_profile__bio__icontains=search)
            )
        
        if location:
            queryset = queryset.filter(caregiver_profile__location__icontains=location)
        
        if service_type:
            queryset = queryset.filter(services__service_type=service_type)
        
        if min_rate:
            queryset = queryset.filter(caregiver_profile__hourly_rate__gte=min_rate)
        
        if max_rate:
            queryset = queryset.filter(caregiver_profile__hourly_rate__lte=max_rate)
        
        return queryset.distinct()

class CaregiverDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.filter(user_type='caregiver')
    serializer_class = CaregiverListSerializer
    permission_classes = [permissions.AllowAny]

class CaregiverServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = CaregiverServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'caregiver':
            return CaregiverService.objects.filter(caregiver=self.request.user)
        return CaregiverService.objects.none()

    def perform_create(self, serializer):
        serializer.save(caregiver=self.request.user)

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        caregiver_id = self.kwargs.get('caregiver_id')
        return Review.objects.filter(caregiver_id=caregiver_id)

    def perform_create(self, serializer):
        caregiver_id = self.kwargs.get('caregiver_id')
        caregiver = User.objects.get(id=caregiver_id, user_type='caregiver')
        
        # Update or create review
        review, created = Review.objects.update_or_create(
            caregiver=caregiver,
            customer=self.request.user,
            defaults={
                'rating': serializer.validated_data['rating'],
                'comment': serializer.validated_data.get('comment', '')
            }
        )
        
        # Update caregiver's average rating
        avg_rating = caregiver.reviews.aggregate(Avg('rating'))['rating__avg']
        caregiver.caregiver_profile.rating = avg_rating or 0
        caregiver.caregiver_profile.total_reviews = caregiver.reviews.count()
        caregiver.caregiver_profile.save()