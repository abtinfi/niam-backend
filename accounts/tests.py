from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from accounts.models import OTPSecret

class ResendEmailVerificationOTPViewTest(APITestCase):
    def setUp(self):
        self.email = 'testuser@example.com'
        self.user = User.objects.create_user(username=self.email, email=self.email, password='testpass', is_active=False)
        self.url = reverse('resend_email_otp')

    def test_resend_otp_for_inactive_user(self):
        response = self.client.post(self.url, {'email': self.email})
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertTrue(OTPSecret.objects.filter(user=self.user, purpose='email_verification').exists())

    def test_resend_otp_for_nonexistent_user(self):
        response = self.client.post(self.url, {'email': 'nouser@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)

    def test_resend_otp_for_active_user(self):
        self.user.is_active = True
        self.user.save()
        response = self.client.post(self.url, {'email': self.email})
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
        # نباید OTP جدید ساخته شود
        self.assertFalse(OTPSecret.objects.filter(user=self.user, purpose='email_verification').exists())
