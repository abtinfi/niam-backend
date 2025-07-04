# core_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# ایمپورت‌های simplejwt برای تعریف دستی

# استفاده از ویوی سفارشی توکن مبتنی بر ایمیل
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView, # اگر نیاز دارید
)
from accounts.custom_jwt import EmailTokenObtainPairView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/accounts/', include('accounts.urls')),
    path('api/files/', include('file_uploader.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG: # یا همیشه اگر از WhiteNoise برای استاتیک استفاده می‌کنید
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
