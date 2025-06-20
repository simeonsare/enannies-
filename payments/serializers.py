from rest_framework import serializers
from .models import Wallet, WalletTransaction, Payment, Earning

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at']

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = '__all__'
        read_only_fields = ['wallet', 'balance_after', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['user', 'status', 'transaction_id', 'gateway_response', 'created_at', 'updated_at', 'processed_at']

class EarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Earning
        fields = '__all__'
        read_only_fields = ['caregiver', 'platform_fee', 'net_amount', 'is_paid', 'paid_at', 'created_at']