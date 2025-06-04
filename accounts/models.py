# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets # برای تولید OTP امن
from datetime import timedelta

class OTPSecret(models.Model):
    PURPOSE_CHOICES = [
        ('password_reset', 'Password Reset'),
        ('email_verification', 'Email Verification'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_secrets')
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='email_verification')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk: # فقط موقع ایجاد جدید
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        """بررسی می‌کند که آیا OTP هنوز معتبر است یا خیر"""
        return not self.is_used and timezone.now() < self.expires_at

    @staticmethod
    def generate_otp():
        """تولید یک OTP 6 رقمی امن"""
        return str(secrets.randbelow(1000000)).zfill(6)

    def __str__(self):
        return f"OTP for {self.user.username} ({self.get_purpose_display()}) - Expires at {self.expires_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']
        # برای اینکه یک کاربر نتواند چند OTP فعال برای یک منظور خاص داشته باشد
        # البته این مورد را در ویو هم مدیریت می‌کنیم که OTP های قبلی غیرفعال شوند
        # unique_together = [['user', 'purpose', 'is_used', 'expires_at']] # این محدودیت ممکن است پیچیده باشد، فعلا از آن صرف نظر می‌کنیم.