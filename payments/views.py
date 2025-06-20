from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Wallet, WalletTransaction, Payment, Earning

@login_required
def wallet_view(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    recent_transactions = wallet.transactions.all()[:10]
    
    context = {
        'wallet': wallet,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'payments/wallet.html', context)

@login_required
def transaction_history(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all()
    
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'wallet': wallet,
    }
    return render(request, 'payments/transactions.html', context)

@login_required
def earnings_view(request):
    if request.user.user_type != 'caregiver':
        messages.error(request, 'Only caregivers can view earnings.')
        return redirect('core:dashboard')
    
    earnings = Earning.objects.filter(caregiver=request.user)
    
    # Calculate totals
    total_earned = sum(e.net_amount for e in earnings if e.is_paid)
    pending_earnings = sum(e.net_amount for e in earnings if not e.is_paid)
    
    paginator = Paginator(earnings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_earned': total_earned,
        'pending_earnings': pending_earnings,
    }
    return render(request, 'payments/earnings.html', context)