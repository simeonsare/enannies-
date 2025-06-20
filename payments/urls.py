from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('wallet/', views.wallet_view, name='wallet'),
    path('transactions/', views.transaction_history, name='transactions'),
    path('earnings/', views.earnings_view, name='earnings'),
]