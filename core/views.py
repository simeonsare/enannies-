from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import User
from bookings.models import BookingRequest
from payments.models import Wallet, Earning

class LandingPageView(TemplateView):
    template_name = 'core/landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get some stats for the landing page
        context.update({
            'total_caregivers': User.objects.filter(user_type='caregiver', is_active=True).count(),
            'total_customers': User.objects.filter(user_type='customer', is_active=True).count(),
            'total_bookings': BookingRequest.objects.filter(status='completed').count(),
            'featured_caregivers': User.objects.filter(
                user_type='caregiver', 
                is_active=True,
                caregiver_profile__available=True
            ).order_by('-caregiver_profile__rating')[:6]
        })
        return context

@login_required
def dashboard_view(request):
    user = request.user
    context = {'user': user}
    
    if user.user_type == 'customer':
        # Customer dashboard data
        recent_bookings = BookingRequest.objects.filter(customer=user)[:5]
        wallet, created = Wallet.objects.get_or_create(user=user)
        
        # Stats
        total_bookings = BookingRequest.objects.filter(customer=user).count()
        upcoming_bookings = BookingRequest.objects.filter(
            customer=user,
            status='accepted',
            start_date__gte=timezone.now().date()
        ).count()
        
        context.update({
            'recent_bookings': recent_bookings,
            'wallet': wallet,
            'total_bookings': total_bookings,
            'upcoming_bookings': upcoming_bookings,
            'dashboard_type': 'customer'
        })
        
    elif user.user_type == 'caregiver':
        # Caregiver dashboard data
        recent_bookings = BookingRequest.objects.filter(caregiver=user)[:5]
        wallet, created = Wallet.objects.get_or_create(user=user)
        
        # Stats
        total_bookings = BookingRequest.objects.filter(caregiver=user).count()
        pending_requests = BookingRequest.objects.filter(
            caregiver=user,
            status='pending'
        ).count()
        
        upcoming_bookings = BookingRequest.objects.filter(
            caregiver=user,
            status='accepted',
            start_date__gte=timezone.now().date()
        ).count()
        
        # Earnings
        earnings = Earning.objects.filter(caregiver=user)
        total_earned = sum(e.net_amount for e in earnings if e.is_paid)
        pending_earnings = sum(e.net_amount for e in earnings if not e.is_paid)
        
        context.update({
            'recent_bookings': recent_bookings,
            'wallet': wallet,
            'total_bookings': total_bookings,
            'pending_requests': pending_requests,
            'upcoming_bookings': upcoming_bookings,
            'total_earned': total_earned,
            'pending_earnings': pending_earnings,
            'dashboard_type': 'caregiver'
        })
        
    elif user.user_type == 'admin':
        # Admin dashboard data
        today = timezone.now().date()
        last_30_days = today - timedelta(days=30)
        
        # Overall stats
        total_users = User.objects.count()
        total_caregivers = User.objects.filter(user_type='caregiver').count()
        total_customers = User.objects.filter(user_type='customer').count()
        total_bookings = BookingRequest.objects.count()
        
        # Recent activity
        recent_bookings = BookingRequest.objects.all()[:10]
        recent_users = User.objects.filter(date_joined__gte=last_30_days)[:10]
        
        # Monthly stats
        monthly_bookings = BookingRequest.objects.filter(
            created_at__gte=last_30_days
        ).count()
        
        context.update({
            'total_users': total_users,
            'total_caregivers': total_caregivers,
            'total_customers': total_customers,
            'total_bookings': total_bookings,
            'monthly_bookings': monthly_bookings,
            'recent_bookings': recent_bookings,
            'recent_users': recent_users,
            'dashboard_type': 'admin'
        })
    
    return render(request, 'core/dashboard.html', context)

def about_view(request):
    return render(request, 'core/about.html')

def contact_view(request):
    return render(request, 'core/contact.html')

def how_it_works_view(request):
    return render(request, 'core/how_it_works.html')