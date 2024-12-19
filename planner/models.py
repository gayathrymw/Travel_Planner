from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Destination(models.Model):
    """
    Comprehensive Destination Model to store a predefined set of destinations
    """
    name = models.CharField(max_length=255, unique=True)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    CLIMATE_CHOICES = [
        ('tropical', 'Tropical'),
        ('desert', 'Desert'),
        ('temperate', 'Temperate'),
        ('alpine', 'Alpine'),
        ('mediterranean', 'Mediterranean'),
    ]
    
    CATEGORY_CHOICES = [
        ('beach', 'Beach'),
        ('city', 'City'),
        ('mountains', 'Mountains'),
        ('historical', 'Historical'),
        ('adventure', 'Adventure'),
        ('cultural', 'Cultural'),
        ('nature', 'Nature'),
    ]
    
    climate = models.CharField(max_length=50, choices=CLIMATE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    # Estimated budget range
    BUDGET_CHOICES = [
        ('low', 'Low (Under Rs. 10000)'),
        ('medium', 'Medium (Rs. 10000-30000)'),
        ('high', 'High (Rs. 30000-80000)'),
        ('luxury', 'Luxury (Over Rs. 80000)'),
    ]
    budget_range = models.CharField(max_length=50, choices=BUDGET_CHOICES)
    
    # Optional geographical data
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name}, {self.country}"

# User Profile Table (Extends Django User Model for additional fields)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    preferred_climate = models.CharField(max_length=50, choices=Destination.CLIMATE_CHOICES, blank=True, null=True)
    preferred_category = models.CharField(max_length=50, choices=Destination.CATEGORY_CHOICES, blank=True, null=True)
    preferred_budget_range = models.CharField(max_length=50, choices=Destination.BUDGET_CHOICES, blank=True, null=True)
    trip_history = models.ManyToManyField('Trip', blank=True)
    gender_c = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer Not to Say')
    ]
    gender = models.CharField(max_length=1, choices=gender_c, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username


# Trips Table
class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, related_name='trips')
    start_date = models.DateField()
    end_date = models.DateField()
    activities = models.TextField()
    accommodation = models.TextField(blank=True, null=True)
    transportation = models.TextField(blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    packing_list = models.TextField(blank=True, null=True)
    travel_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Trip to {self.destination.name if self.destination else 'Unknown'} ({self.start_date} - {self.end_date})"
      

# Recommendation Data Table
class RecommendationData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'destination')

    def __str__(self):
        return f"{self.user.username} -> {self.destination.name}: {self.rating}"