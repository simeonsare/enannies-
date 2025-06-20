from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('how-it-works/', views.how_it_works_view, name='how_it_works'),
]