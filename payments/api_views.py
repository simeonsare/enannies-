from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Wallet, WalletTransaction, Payment, Earning
from .serializers import WalletSerializer, WalletTransactionSerializer, PaymentSerializer, EarningSerializer
from bookings.models import BookingRequest

class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        wallet, created = Wallet.objects.get_or_create(user=self.request.user)
        return wallet

class WalletTransactionListView(generics.ListAPIView):
    serializer_class = WalletTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        wallet, created = Wallet.objects.get_or_create(user=self.request.user)
        return wallet.transactions.all()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def wallet_topup(request):
    amount = request.data.get('amount')
    payment_method = request.data.get('payment_method', 'mpesa')
    
    if not amount or amount <= 0:
        return Response({'error': 'Invalid amount'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create payment record
    payment = Payment.objects.create(
        user=request.user,
        amount=amount,
        payment_method=payment_method,
        description=f"Wallet top-up - ${amount}",
        status='processing'
    )
    
    # In a real implementation, you would integrate with payment gateway here
    # For now, we'll simulate successful payment
    payment.mark_completed()
    
    # Credit user's wallet
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    wallet.credit(amount, f"Wallet top-up via {payment_method}")
    
    return Response({
        'message': 'Wallet topped up successfully',
        'payment_id': payment.id,
        'new_balance': wallet.balance
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def process_booking_payment(request, booking_id):
    booking = get_object_or_404(BookingRequest, id=booking_id, customer=request.user)
    
    if booking.status != 'accepted':
        return Response({'error': 'Booking must be accepted before payment'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if already paid
    if booking.payments.filter(status='completed').exists():
        return Response({'error': 'Booking already paid'}, status=status.HTTP_400_BAD_REQUEST)
    
    payment_method = request.data.get('payment_method', 'wallet')
    
    if payment_method == 'wallet':
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        
        if not wallet.can_debit(booking.total_amount):
            return Response({'error': 'Insufficient wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Debit customer's wallet
        wallet.debit(booking.total_amount, f"Payment for booking #{booking.id}")
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            booking=booking,
            amount=booking.total_amount,
            payment_method=payment_method,
            description=f"Payment for booking #{booking.id}",
            status='completed'
        )
        
        # Create earning record for caregiver
        earning = Earning.objects.create(
            caregiver=booking.caregiver,
            booking=booking,
            gross_amount=booking.total_amount
        )
        earning.calculate_platform_fee()
        
        return Response({
            'message': 'Payment processed successfully',
            'payment_id': payment.id
        })
    
    else:
        # Handle other payment methods (implement payment gateway integration)
        return Response({'error': 'Payment method not supported yet'}, status=status.HTTP_400_BAD_REQUEST)

class EarningListView(generics.ListAPIView):
    serializer_class = EarningSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.user_type == 'caregiver':
            return Earning.objects.filter(caregiver=self.request.user)
        return Earning.objects.none()