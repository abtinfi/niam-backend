from django.urls import path
from .views import (
    FileUploadView,
    UserFileListView,
    CarbonEntryCreateView,
    ExcelUploadParseView,
    CarbonSummaryView,
    CarbonChartView
)

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('list/', UserFileListView.as_view(), name='file-list'),
    path('carbon/create/', CarbonEntryCreateView.as_view(), name='carbon-create'),
    path('carbon/excel/', ExcelUploadParseView.as_view(), name='carbon-excel-upload'),
    path('carbon/summary/<int:pk>/', CarbonSummaryView.as_view(), name='carbon-summary'),
    path('carbon/charts/<int:pk>/', CarbonChartView.as_view(), name='carbon-charts'),
]
