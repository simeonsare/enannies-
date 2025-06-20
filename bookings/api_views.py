from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import BookingRequest, BookingMessage
from .serializers import BookingRequestSerializer, BookingMessageSerializer, BookingUpdateSerializer
from accounts.models import User

class BookingListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'customer':
            return BookingRequest.objects.filter(customer=user)
        elif user.user_type == 'caregiver':
            return BookingRequest.objects.filter(caregiver=user)
        return BookingRequest.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'customer':
            raise permissions.PermissionDenied("Only customers can create bookings")
        serializer.save(customer=self.request.user)

class BookingDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = BookingRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return BookingRequest.objects.filter(
            models.Q(customer=user) | models.Q(caregiver=user)
        )
    
    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return BookingUpdateSerializer
        return BookingRequestSerializer

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def respond_to_booking(request, booking_id):
    booking = get_object_or_404(BookingRequest, id=booking_id, caregiver=request.user)
    
    if booking.status != 'pending':
        return Response({'error': 'Booking is no longer pending'}, status=status.HTTP_400_BAD_REQUEST)
    
    response_status = request.data.get('status')
    message = request.data.get('message', '')
    
    if response_status not in ['accepted', 'rejected']:
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    
    booking.status = response_status
    booking.caregiver_response_message = message
    booking.responded_at = timezone.now()
    booking.save()
    
    return Response(BookingRequestSerializer(booking).data)

class BookingMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = BookingMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        booking_id = self.kwargs.get('booking_id')
        booking = get_object_or_404(BookingRequest, id=booking_id)
        
        # Check if user is part of this booking
        user = self.request.user
        if user not in [booking.customer, booking.caregiver]:
            return BookingMessage.objects.none()
        
        return booking.messages.all()
    
    def perform_create(self, serializer):
        booking_id = self.kwargs.get('booking_id')
        booking = get_object_or_404(BookingRequest, id=booking_id)
        
        # Check if user is part of this booking
        user = self.request.user
        if user not in [booking.customer, booking.caregiver]:
            raise permissions.PermissionDenied("You cannot message in this booking")
        
        serializer.save(sender=self.request.user, booking=booking)