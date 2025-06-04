# accounts/serializers.py
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm Password")

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "رمز عبور و تایید آن یکسان نیستند."}) # پیام فارسی

        # این اعتبارسنجی برای ثبت نام (create) صحیح است.
        # اگر برای ویرایش (update) استفاده شود، باید چک شود که آیا ایمیل تغییر کرده است یا خیر.
        # if self.instance and self.instance.email == attrs.get('email'):
        # pass # ایمیل تغییر نکرده، نیازی به بررسی تکراری بودن نیست
        # elif User.objects.filter(email__iexact=attrs.get('email')).exists():
        # raise serializers.ValidationError({"email": "کاربری با این ایمیل قبلا ثبت نام کرده است."})
        if not self.instance and User.objects.filter(email__iexact=attrs.get('email')).exists(): # فقط برای create
             raise serializers.ValidationError({"email": "کاربری با این ایمیل قبلا ثبت نام کرده است."})
        # اگر برای آپدیت هم می‌خواهید استفاده کنید و ایمیل قابل تغییر است:
        if self.instance and 'email' in attrs and self.instance.email != attrs.get('email'):
            if User.objects.filter(email__iexact=attrs.get('email')).exists():
                raise serializers.ValidationError({"email": "کاربری با این ایمیل قبلا ثبت نام کرده است."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            is_active=False  # کاربر به صورت غیرفعال ایجاد می‌شود
        )
        user.set_password(validated_data['password'])

        user.first_name = validated_data.get('first_name', "") # استفاده از .get برای جلوگیری از KeyError
        user.last_name = validated_data.get('last_name', "")  # استفاده از .get

        user.save()
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        # اعتبارسنجی وجود کاربر از اینجا حذف شد تا با منطق PasswordResetRequestView
        # (که برای جلوگیری از شمارش کاربر، همیشه پیام موفقیت عمومی برمی‌گرداند) هماهنگ باشد.
        # خود EmailField فرمت ایمیل را چک می‌کند.
        return value.lower() # بهتر است ایمیل به حروف کوچک تبدیل شود

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=6, max_length=6)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("کاربری با این ایمیل یافت نشد.")
        return value.lower()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "رمز عبور و تایید آن یکسان نیستند."})
        return attrs

class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=6, max_length=6)

    def validate_email(self, value):
        try:
            user = User.objects.get(email__iexact=value)
            if user.is_active:
                raise serializers.ValidationError("این حساب قبلا فعال شده است.")
        except User.DoesNotExist:
            raise serializers.ValidationError("کاربری با این ایمیل یافت نشد یا حساب هنوز ایجاد نشده است.")
        return value.lower()