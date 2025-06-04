from rest_framework import serializers
from .models import UploadedFile

class UploadedFileSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UploadedFile
        fields = ['id', 'user', 'user_username', 'file', 'uploaded_at', 'file_name', 'file_type']
        read_only_fields = ['user', 'uploaded_at', 'file_name', 'file_type', 'user_username'] 
    def validate_file(self, value):
        ext = value.name.split('.')[-1].lower()
        if ext not in ['csv', 'xls', 'xlsx']:
            raise serializers.ValidationError("Enter a valid file. Supported formats are: csv, xls, xlsx.")
        # اینجا می‌توانیم محدودیت حجم فایل هم اضافه کنیم
        # if value.size > MAX_UPLOAD_SIZE:
        #     raise serializers.ValidationError(f"حجم فایل بیش از حد مجاز است ({MAX_UPLOAD_SIZE} بایت).")
        return value