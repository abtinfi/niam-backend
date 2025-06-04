from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser 
from rest_framework.response import Response
from .models import UploadedFile
from .serializers import UploadedFileSerializer

class FileUploadView(generics.CreateAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated] 
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        # اینجا می‌توانیم پس از ذخیره فایل، کارهای مربوط به هوش مصنوعی را شروع کنیم (در مراحل بعدی)

class UserFileListView(generics.ListAPIView):
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UploadedFile.objects.all() 
        return UploadedFile.objects.filter(user=user)