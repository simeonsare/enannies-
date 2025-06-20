from django.urls import path
from . import views

app_name = 'caregivers'

urlpatterns = [
    path('', views.caregiver_list, name='list'),
    path('<int:caregiver_id>/', views.caregiver_detail, name='detail'),
    path('<int:caregiver_id>/review/', views.add_review, name='add_review'),
]