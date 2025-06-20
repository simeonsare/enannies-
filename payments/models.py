from django.db import models
from django.utils import timezone
from accounts.models import User
from bookings.models import BookingRequest

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s Wallet - ${self.balance}"
    
    def can_debit(self, amount):
        return self.balance >= amount
    
    def debit(self, amount, description=""):
        if self.can_debit(amount):
            self.balance -= amount
            self.save()
            
            # Create transaction record
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type='debit',
                amount=amount,
                description=description,
                balance_after=self.balance
            )
            return True
        return False
    
    def credit(self, amount, description=""):
        self.balance += amount
        self.save()
        
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type='credit',
            amount=amount,
            description=description,
            balance_after=self.balance
        )

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.transaction_type.title()} - ${self.amount} - {self.wallet.user.get_full_name()}"

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('wallet', 'Wallet'),
        ('mpesa', 'M-Pesa'),
        ('stripe', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    booking = models.ForeignKey(BookingRequest, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment gateway references
    transaction_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Metadata
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment #{self.id} - {self.user.get_full_name()} - ${self.amount}"
    
    def mark_completed(self):
        self.status = 'completed'
        self.processed_at = timezone.now()
        self.save()
    
    def mark_failed(self):
        self.status = 'failed'
        self.processed_at = timezone.now()
        self.save()

class Earning(models.Model):
    caregiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earnings')
    booking = models.OneToOneField(BookingRequest, on_delete=models.CASCADE, related_name='earning')
    
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Earning for {self.caregiver.get_full_name()} - ${self.net_amount}"
    
    def calculate_platform_fee(self, rate=0.10):
        """Calculate platform fee (default 10%)"""
        self.platform_fee = self.gross_amount * rate
        self.net_amount = self.gross_amount - self.platform_fee
        self.save()
    
    def mark_paid(self):
        self.is_paid = True
        self.paid_at = timezone.now()
        self.save()
        
        # Credit caregiver's wallet
        wallet, created = Wallet.objects.get_or_create(user=self.caregiver)
        wallet.credit(
            self.net_amount,
            f"Earning from booking #{self.booking.id}"
        )