from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import User, CustomerProfile, CaregiverProfile
from .forms import UserRegistrationForm, CustomerProfileForm, CaregiverProfileForm


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        
        # Create profile based on user type
        if user.user_type == 'customer':
            CustomerProfile.objects.create(user=user)
        elif user.user_type == 'caregiver':
            CaregiverProfile.objects.create(user=user)
        
        messages.success(self.request, 'Registration successful! Please log in.')
        return response

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing')

@login_required
def profile_view(request):
    user = request.user
    profile = None
    
    if user.user_type == 'customer':
        profile = getattr(user, 'customer_profile', None)
    elif user.user_type == 'caregiver':
        profile = getattr(user, 'caregiver_profile', None)
    
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile_view(request):
    user = request.user
    
    if user.user_type == 'customer':
        profile = getattr(user, 'customer_profile', None)
        if not profile:
            profile = CustomerProfile.objects.create(user=user)
        
        if request.method == 'POST':
            form = CustomerProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:profile')
        else:
            form = CustomerProfileForm(instance=profile)
    
    elif user.user_type == 'caregiver':
        profile = getattr(user, 'caregiver_profile', None)
        if not profile:
            profile = CaregiverProfile.objects.create(user=user)
        
        if request.method == 'POST':
            form = CaregiverProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('accounts:profile')
        else:
            form = CaregiverProfileForm(instance=profile)
    
    else:
        messages.error(request, 'Invalid user type.')
        return redirect('accounts:profile')
    
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'accounts/edit_profile.html', context)