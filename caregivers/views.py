from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from accounts.models import User

def caregiver_list(request):
    caregivers = User.objects.filter(user_type='caregiver', is_active=True)
    
    # Search and filter
    search_query = request.GET.get('search', '')
    location = request.GET.get('location', '')
    service_type = request.GET.get('service_type', '')
    min_rate = request.GET.get('min_rate', '')
    max_rate = request.GET.get('max_rate', '')
    
    if search_query:
        caregivers = caregivers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(caregiver_profile__bio__icontains=search_query)
        )
    
    if location:
        caregivers = caregivers.filter(caregiver_profile__location__icontains=location)
    
    if service_type:
        caregivers = caregivers.filter(services__service_type=service_type)
    
    if min_rate:
        caregivers = caregivers.filter(caregiver_profile__hourly_rate__gte=min_rate)
    
    if max_rate:
        caregivers = caregivers.filter(caregiver_profile__hourly_rate__lte=max_rate)
    
    # Pagination
    paginator = Paginator(caregivers.distinct(), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'location': location,
        'service_type': service_type,
        'min_rate': min_rate,
        'max_rate': max_rate,
    }
    return render(request, 'caregivers/list.html', context)

def caregiver_detail(request, caregiver_id):
    caregiver = get_object_or_404(User, id=caregiver_id, user_type='caregiver')
    #caregiver.certifications_list = {{User.caregiver.certifications}}.split(",") if{{ User.caregiver.certifications}} else []

    reviews = caregiver.reviews.all().order_by('-created_at')[:10]
    
    context = {
        'caregiver': caregiver,
        'reviews': reviews,
        'caregiver_id': caregiver_id, 
    }
    return render(request, 'caregivers/detail.html', context)

@login_required
def add_review(request, caregiver_id):
    caregiver = get_object_or_404(User, id=caregiver_id, user_type='caregiver')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and 1 <= int(rating) <= 5:
            from .models import Review
            review, created = Review.objects.get_or_create(
                caregiver=caregiver,
                customer=request.user,
                defaults={'rating': rating, 'comment': comment}
            )
            
            if not created:
                review.rating = rating
                review.comment = comment
                review.save()
            
            # Update caregiver's average rating
            avg_rating = caregiver.reviews.aggregate(Avg('rating'))['rating__avg']
            caregiver.caregiver_profile.rating = avg_rating or 0
            caregiver.caregiver_profile.total_reviews = caregiver.reviews.count()
            caregiver.caregiver_profile.save()
    
    return redirect('caregivers:detail', caregiver_id=caregiver_id)