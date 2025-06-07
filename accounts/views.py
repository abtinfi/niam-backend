# accounts/views.py
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTPSecret
from .serializers import (
    EmailVerificationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserSerializer,
)
from .email_utils import send_otp_email


class ResendEmailVerificationOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"error": "ایمیل الزامی است."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email__iexact=email, is_active=False)
        except User.DoesNotExist:
            # پیام عمومی برای جلوگیری از افشای وجود کاربر
            return Response({"message": "اگر ایمیل شما در سیستم موجود باشد و هنوز تایید نشده باشد، کد تایید ارسال خواهد شد."}, status=status.HTTP_200_OK)

        # غیرفعال کردن OTP های فعال قبلی برای تایید ایمیل همین کاربر
        OTPSecret.objects.filter(
            user=user,
            purpose='email_verification',
            is_used=False,
            expires_at__gt=timezone.now()
        ).update(expires_at=timezone.now())

        otp_code = OTPSecret.generate_otp()
        OTPSecret.objects.create(user=user, otp_code=otp_code, purpose='email_verification')

        if send_otp_email(user.email, otp_code, user.username, purpose='email_verification'):
            return Response({"message": "اگر ایمیل شما در سیستم موجود باشد و هنوز تایید نشده باشد، کد تایید ارسال خواهد شد."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "خطا در ارسال ایمیل. لطفا بعدا تلاش کنید."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# accounts/views.py
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTPSecret
from .serializers import (
    EmailVerificationSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserSerializer,
)
from .email_utils import send_otp_email


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()  # UserSerializer باید is_active=False را تنظیم کند

        # غیرفعال کردن OTP های فعال قبلی برای تایید ایمیل همین کاربر
        OTPSecret.objects.filter(
            user=user,
            purpose='email_verification',
            is_used=False,
            expires_at__gt=timezone.now()
        ).update(expires_at=timezone.now())

        otp_code = OTPSecret.generate_otp()
        OTPSecret.objects.create(user=user, otp_code=otp_code, purpose='email_verification')

        send_otp_email(user.email, otp_code, user.username, purpose='email_verification')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "ثبت‌نام موفقیت‌آمیز بود. لطفا ایمیل خود را برای کد فعال‌سازی بررسی کنید."},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class EmailVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp']

            try:
                user = User.objects.get(email__iexact=email, is_active=False)
                otp_entry = OTPSecret.objects.get(
                    user=user,
                    otp_code=otp_code,
                    purpose='email_verification',
                    is_used=False
                )
            except User.DoesNotExist:
                return Response({"error": "کاربر یافت نشد یا حساب قبلا فعال شده است."}, status=status.HTTP_400_BAD_REQUEST)
            except OTPSecret.DoesNotExist:
                return Response({"error": "کد تایید نامعتبر یا منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)

            if not otp_entry.is_valid():
                otp_entry.is_used = True # علامت زدن OTP منقضی شده به عنوان استفاده شده
                otp_entry.save()
                return Response({"error": "کد تایید منقضی شده است. لطفا دوباره درخواست کد کنید."}, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()

            otp_entry.is_used = True
            otp_entry.save()

            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user, context=self.get_serializer_context()).data
            # اطمینان از عدم بازگشت فیلدهای حساس (اگرچه UserSerializer باید این را مدیریت کند)
            user_data.pop('password', None)

            return Response({
                "message": "ایمیل شما با موفقیت تایید شد. حساب شما فعال است.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": user_data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                return Response({"message": "اگر ایمیل شما در سیستم موجود باشد، کد تایید ارسال خواهد شد."}, status=status.HTTP_200_OK)

            # غیرفعال کردن OTP های فعال قبلی برای ریست پسورد همین کاربر
            OTPSecret.objects.filter(
                user=user,
                purpose='password_reset', # <--- تغییر اعمال شده
                is_used=False,
                expires_at__gt=timezone.now()
            ).update(expires_at=timezone.now())

            otp_code = OTPSecret.generate_otp()
            OTPSecret.objects.create(user=user, otp_code=otp_code, purpose='password_reset') # <--- تغییر اعمال شده

            if send_otp_email(user.email, otp_code, user.username, purpose='password_reset'): # <--- تغییر اعمال شده
                return Response({"message": "اگر ایمیل شما در سیستم موجود باشد، کد تایید ارسال خواهد شد."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "خطا در ارسال ایمیل. لطفا بعدا تلاش کنید."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']

            try:
                user = User.objects.get(email__iexact=email)
                otp_entry = OTPSecret.objects.get(
                    user=user,
                    otp_code=otp_code,
                    purpose='password_reset', # <--- تغییر اعمال شده
                    is_used=False
                )
            except User.DoesNotExist:
                return Response({"error": "اطلاعات نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)
            except OTPSecret.DoesNotExist:
                return Response({"error": "کد تایید نامعتبر یا منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)

            if not otp_entry.is_valid():
                otp_entry.is_used = True # علامت زدن OTP منقضی شده به عنوان استفاده شده
                otp_entry.save()
                return Response({"error": "کد تایید منقضی شده است."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            otp_entry.is_used = True
            otp_entry.save()

            return Response({"message": "رمز عبور شما با موفقیت تغییر کرد."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)