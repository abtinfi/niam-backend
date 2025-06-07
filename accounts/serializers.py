# accounts/serializers.py
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    full_name = serializers.CharField(write_only=True, required=True)
    full_name_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'full_name', 'full_name_display')
        extra_kwargs = {
            'email': {'required': True}
        }

    def get_full_name_display(self, obj):
        return obj.first_name

    def validate(self, attrs):
        if not self.instance and User.objects.filter(email__iexact=attrs.get('email')).exists(): # فقط برای create
            raise serializers.ValidationError({"email": "کاربری با این ایمیل قبلا ثبت نام کرده است."})
        if self.instance and 'email' in attrs and self.instance.email != attrs.get('email'):
            if User.objects.filter(email__iexact=attrs.get('email')).exists():
                raise serializers.ValidationError({"email": "کاربری با این ایمیل قبلا ثبت نام کرده است."})
        return attrs

    def create(self, validated_data):
        # ایمیل به عنوان یوزرنیم استفاده شود
        full_name = validated_data.get('full_name', "").strip()
        # همه full_name را در first_name قرار می‌دهیم و last_name خالی می‌ماند
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            is_active=False
        )
        user.set_password(validated_data['password'])
        user.first_name = full_name
        user.last_name = ""
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