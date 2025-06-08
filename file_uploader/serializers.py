from rest_framework import serializers
from .models import UploadedFile, CarbonEntry

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['id', 'file', 'file_name', 'file_type', 'uploaded_at']

class CarbonEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonEntry
        fields = [
            'id',
            'user',
            'date_created',
            'kilometers_per_week',
            'electricity_per_month',
            'short_flights_per_year',
            'long_flights_per_year',
            'recycling',
            'diet_type',
            'total_emissions',
            'classification',
        ]
        read_only_fields = ['user', 'date_created', 'total_emissions', 'classification']
