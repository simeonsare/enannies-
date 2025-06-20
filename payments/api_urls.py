from django.urls import path
from . import api_views

urlpatterns = [
    path('wallet/', api_views.WalletDetailView.as_view(), name='wallet_detail'),
    path('wallet/transactions/', api_views.WalletTransactionListView.as_view(), name='wallet_transactions'),
    path('wallet/topup/', api_views.wallet_topup, name='wallet_topup'),
    path('bookings/<int:booking_id>/pay/', api_views.process_booking_payment, name='booking_payment'),
    path('earnings/', api_views.EarningListView.as_view(), name='earnings'),
]