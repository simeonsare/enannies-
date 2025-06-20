from rest_framework import serializers
from .models import CaregiverService, CaregiverAvailability, Review
from accounts.serializers import UserSerializer

class CaregiverServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaregiverService
        fields = '__all__'
        read_only_fields = ['caregiver']

class CaregiverAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CaregiverAvailability
        fields = '__all__'
        read_only_fields = ['caregiver']

class ReviewSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['customer', 'created_at']

class CaregiverListSerializer(serializers.ModelSerializer):
    services = CaregiverServiceSerializer(many=True, read_only=True)
    caregiver_profile = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'first_name', 'last_name', 'services', 'caregiver_profile', 'average_rating']
    
    def get_caregiver_profile(self, obj):
        from accounts.serializers import CaregiverProfileSerializer
        return CaregiverProfileSerializer(obj.caregiver_profile).data
    
    def get_average_rating(self, obj):
        return obj.caregiver_profile.rating if hasattr(obj, 'caregiver_profile') else 0