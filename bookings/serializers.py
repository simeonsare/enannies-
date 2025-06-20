from rest_framework import serializers
from .models import BookingRequest, BookingMessage
from accounts.serializers import UserSerializer

class BookingRequestSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    caregiver = UserSerializer(read_only=True)
    caregiver_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = BookingRequest
        fields = '__all__'
        read_only_fields = ['customer', 'total_amount', 'status', 'created_at', 'updated_at', 'responded_at']
    
    def validate(self, attrs):
        # Calculate total amount
        duration = attrs.get('duration_hours', 0)
        hourly_rate = attrs.get('hourly_rate', 0)
        attrs['total_amount'] = duration * hourly_rate
        return attrs
    
    def create(self, validated_data):
        caregiver_id = validated_data.pop('caregiver_id')
        validated_data['caregiver_id'] = caregiver_id
        return super().create(validated_data)

class BookingMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = BookingMessage
        fields = '__all__'
        read_only_fields = ['sender', 'created_at']

class BookingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingRequest
        fields = ['status', 'caregiver_response_message']
    
    def validate_status(self, value):
        if self.instance.status == 'completed':
            raise serializers.ValidationError("Cannot update completed booking")
        return value