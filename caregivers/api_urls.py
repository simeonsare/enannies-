from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.CaregiverListAPIView.as_view(), name='caregiver_list'),
    path('<int:pk>/', api_views.CaregiverDetailAPIView.as_view(), name='caregiver_detail'),
    path('services/', api_views.CaregiverServiceListCreateView.as_view(), name='caregiver_services'),
    path('<int:caregiver_id>/reviews/', api_views.ReviewListCreateView.as_view(), name='caregiver_reviews'),
]