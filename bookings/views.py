from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BookingRequest, BookingMessage
from .forms import BookingRequestForm, BookingMessageForm
from accounts.models import User

@login_required
def booking_list(request):
    user = request.user
    
    if user.user_type == 'customer':
        bookings = BookingRequest.objects.filter(customer=user)
    elif user.user_type == 'caregiver':
        bookings = BookingRequest.objects.filter(caregiver=user)
    else:
        bookings = BookingRequest.objects.none()
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    paginator = Paginator(bookings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'user_type': user.user_type,
    }
    return render(request, 'bookings/list.html', context)

@login_required
def create_booking(request, caregiver_id):
    if request.user.user_type != 'customer':
        messages.error(request, 'Only customers can create bookings.')
        return redirect('core:dashboard')
    
    caregiver = get_object_or_404(User, id=caregiver_id, user_type='caregiver')
    
    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.caregiver = caregiver
            booking.hourly_rate = caregiver.caregiver_profile.hourly_rate
            booking.total_amount = booking.duration_hours * booking.hourly_rate
            booking.save()
            
            messages.success(request, 'Booking request sent successfully!')
            return redirect('bookings:detail', booking_id=booking.id)
    else:
        form = BookingRequestForm()
    
    context = {
        'form': form,
        'caregiver': caregiver,
    }
    return render(request, 'bookings/create.html', context)

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(BookingRequest, id=booking_id)
    user = request.user
    
    # Check if user has access to this booking
    if user not in [booking.customer, booking.caregiver]:
        messages.error(request, 'You do not have access to this booking.')
        return redirect('core:dashboard')
    
    # Handle caregiver response
    if request.method == 'POST' and user == booking.caregiver and booking.status == 'pending':
        response_status = request.POST.get('status')
        response_message = request.POST.get('message', '')
        
        if response_status in ['accepted', 'rejected']:
            booking.status = response_status
            booking.caregiver_response_message = response_message
            booking.responded_at = timezone.now()
            booking.save()
            
            action = 'accepted' if response_status == 'accepted' else 'rejected'
            messages.success(request, f'Booking {action} successfully!')
            return redirect('bookings:detail', booking_id=booking.id)
    
    # Get messages
    booking_messages = booking.messages.all()
    
    # Handle new message
    message_form = BookingMessageForm()
    if request.method == 'POST' and 'send_message' in request.POST:
        message_form = BookingMessageForm(request.POST)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.booking = booking
            message.sender = user
            message.save()
            messages.success(request, 'Message sent!')
            return redirect('bookings:detail', booking_id=booking.id)
    
    context = {
        'booking': booking,
        'booking_messages': booking_messages,
        'message_form': message_form,
        'user_type': user.user_type,
        'can_respond': user == booking.caregiver and booking.status == 'pending',
    }
    return render(request, 'bookings/detail.html', context)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(BookingRequest, id=booking_id)
    user = request.user
    
    # Check permissions
    if user not in [booking.customer, booking.caregiver]:
        messages.error(request, 'You do not have access to this booking.')
        return redirect('core:dashboard')
    
    if not booking.can_be_cancelled:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('bookings:detail', booking_id=booking.id)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully!')
        return redirect('bookings:list')
    
    context = {'booking': booking}
    return render(request, 'bookings/cancel.html', context)