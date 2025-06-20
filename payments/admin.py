from django.contrib import admin
from .models import Wallet, WalletTransaction, Payment, Earning

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'created_at', 'updated_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    list_filter = ['created_at']

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'transaction_type', 'amount', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['wallet__user__first_name', 'wallet__user__last_name', 'description']
    readonly_fields = ['created_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at', 'processed_at']

@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ['caregiver', 'booking', 'gross_amount', 'platform_fee', 'net_amount', 'is_paid']
    list_filter = ['is_paid', 'created_at']
    search_fields = ['caregiver__first_name', 'caregiver__last_name']
    readonly_fields = ['created_at', 'paid_at']