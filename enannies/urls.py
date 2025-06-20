from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import LandingPageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LandingPageView.as_view(), name='landing'),
    path('accounts/', include('accounts.urls')),
    path('api/auth/', include('accounts.api_urls')),
    path('caregivers/', include('caregivers.urls')),
    path('api/caregivers/', include('caregivers.api_urls')),
    path('bookings/', include(('bookings.urls'),namespace='booking')),
    path('api/bookings/', include('bookings.api_urls')),
    path('payments/', include('payments.urls')),
    path('api/payments/', include('payments.api_urls')),
    path('dashboard/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)