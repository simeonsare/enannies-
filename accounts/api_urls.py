from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

urlpatterns = [
    path('register/', api_views.register, name='api_register'),
    path('login/', api_views.login, name='api_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', api_views.ProfileView.as_view(), name='api_profile'),
]