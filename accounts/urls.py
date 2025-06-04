from django.urls import path
from .views import (
    RegisterView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    EmailVerifyView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('verify-email/', EmailVerifyView.as_view(), name='auth_verify_email'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]