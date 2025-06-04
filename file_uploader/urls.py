from django.urls import path
from .views import FileUploadView, UserFileListView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('list/', UserFileListView.as_view(), name='file-list'),
]