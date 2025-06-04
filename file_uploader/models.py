from django.db import models
from django.contrib.auth.models import User
import os

def get_upload_path(instance, filename):
    return os.path.join('uploads', str(instance.user.username), filename)

class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    file = models.FileField(upload_to=get_upload_path) 
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255, blank=True) 
    file_type = models.CharField(max_length=10, blank=True) 

    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = os.path.basename(self.file.name)
        if not self.file_type and '.' in self.file_name:
            self.file_type = self.file_name.split('.')[-1].lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file_name} by {self.user.username}"

    class Meta:
        ordering = ['-uploaded_at']