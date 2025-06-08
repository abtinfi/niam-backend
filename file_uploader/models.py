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

class CarbonEntry(models.Model):
    DIET_CHOICES = [
        ('omnivore', 'Omnivore'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carbon_entries')
    date_created = models.DateTimeField(auto_now_add=True)

    # Inputs
    kilometers_per_week = models.FloatField(help_text="Average kilometers driven per week")
    electricity_per_month = models.FloatField(help_text="Electricity usage in kWh per month")
    short_flights_per_year = models.IntegerField()
    long_flights_per_year = models.IntegerField()
    recycling = models.BooleanField(help_text="Does the user recycle?")
    diet_type = models.CharField(max_length=20, choices=DIET_CHOICES)

    # Outputs
    total_emissions = models.FloatField(null=True, blank=True, help_text="Calculated carbon footprint in kg/year")
    classification = models.CharField(max_length=10, blank=True, help_text="Low / Average / High")

    def calculate_emissions(self):
        # Calculate each component
        driving = self.kilometers_per_week * 52 * 0.21
        electricity = self.electricity_per_month * 12 * 0.4
        flights = self.short_flights_per_year * 250 + self.long_flights_per_year * 1100
        recycling = 0 if self.recycling else 150

        if self.diet_type == 'omnivore':
            diet = 1000
        elif self.diet_type == 'vegetarian':
            diet = 600
        else:
            diet = 300

        # Total
        total = driving + electricity + flights + recycling + diet
        self.total_emissions = round(total, 2)

        # Classification
        if total < 3000:
            self.classification = "Low"
        elif 3000 <= total <= 6000:
            self.classification = "Average"
        else:
            self.classification = "High"

        return self.total_emissions

    def save(self, *args, **kwargs):
        self.calculate_emissions()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.date_created.date()} - {self.total_emissions} kg"
