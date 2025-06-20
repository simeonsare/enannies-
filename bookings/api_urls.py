from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.BookingListCreateView.as_view(), name='booking_list_create'),
    path('<int:pk>/', api_views.BookingDetailView.as_view(), name='booking_detail'),
    path('<int:booking_id>/respond/', api_views.respond_to_booking, name='booking_respond'),
    path('<int:booking_id>/messages/', api_views.BookingMessageListCreateView.as_view(), name='booking_messages'),
]