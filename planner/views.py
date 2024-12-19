from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Trip, UserProfile, Destination, RecommendationData
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from googleplaces import GooglePlaces
from django.conf import settings

# Home Page View
def home(request):
    return render(request, 'home.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password) 
        #print(user)

        if user is not None:
            login(request, user)
            return redirect('profile') 
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')

@login_required
def logout_user(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        #print("Full POST data:", request.POST)
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate the form data
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'register.html')

        # Save the user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        new_user = authenticate(username=username, password=password)
        if new_user is not None:
            login(request, new_user)

        messages.success(request, 'Registration successful.')
        return redirect('profile') 

    return render(request, 'register.html') 

# User Profile View
@login_required
def profile(request):
    user_trips = Trip.objects.filter(user=request.user) 
    return render(request, 'profile.html', {'trips': user_trips,'username': request.user.username})

# User Details View
@login_required
def user_details(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user) 

    if request.method == 'POST':
        # Update profile fields with POST data
        profile.first_name = request.POST.get('first_name', profile.first_name)
        profile.gender = request.POST.get('gender', profile.gender)
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.location = request.POST.get('location', profile.location)
        profile.preferred_climate = request.POST.get('preferred_climate', profile.preferred_climate)
        profile.preferred_category = request.POST.get('preferred_category', profile.preferred_category)
        profile.preferred_budget_range = request.POST.get('preferred_budget_range', profile.preferred_budget_range)
        
        profile.save() 

        messages.success(request, 'Your details have been updated successfully!')
        return redirect('user_details')  # Redirect to the same page after POST

    return render(request, 'user_details.html', { 
        'username': request.user.username,
        'email': request.user.email,
        'profile': profile,
        'destination_climate_choices': Destination.CLIMATE_CHOICES, 
        'destination_category_choices': Destination.CATEGORY_CHOICES,
        'destination_budget_choices': Destination.BUDGET_CHOICES,
    })

# My Trips View
@login_required
def my_trips(request):
    trips = Trip.objects.filter(user=request.user)
    return render(request, 'my_trips.html', {'trips': trips})

def enrich_destination_details(destination_name, budget=None):
    """
    Fetch detailed destination information using Google Places API
    """
    google_places = GooglePlaces(settings.GOOGLE_PLACES_API_KEY)
    
    try:
        # Search for the destination
        query_result = google_places.text_search(query=destination_name)
        
        if query_result.places:
            place = query_result.places[0]
            place.get_details()  # Fetch full place details
            
            #print(place.details)
            #print(place.geo_location)

            latitude = float(place.geo_location.get('lat', 0))
            longitude = float(place.geo_location.get('lng', 0))

            # Extract rich information
            return {
                'name': place.name,
                'country': place.details.get('formatted_address', '').split(', ')[-1],
                'latitude': latitude,
                'longitude': longitude,
                'types': place.details.get('types', []),
                'climate': _infer_climate(latitude, longitude),
                'budget_range': _estimate_budget_range(budget)
            }
            
    except Exception as e:
        # Log the error, return minimal information
        print(f"API Enrichment Error: {e}")
    
    return None

def _infer_climate(latitude, longitude):
    """
    Infer the climate based on latitude and rough rules.
    """
    if -23.5 <= latitude <= 23.5:
        return 'tropical'
    elif 23.5 < latitude <= 40 or -40 <= latitude < -23.5:
        return 'temperate'
    elif 40 < latitude <= 60 or -60 <= latitude < -40:
        return 'alpine'
    elif 30 < latitude <= 45 or -30 >= latitude > -45 and _is_mediterranean(longitude):
        return 'mediterranean'
    elif 60 < latitude <= 90 or -90 <= latitude < -60:
        return 'polar'
    else:
        return 'desert'

def _is_mediterranean(longitude):
    """
    Check if the longitude roughly aligns with Mediterranean regions.
    """
    mediterranean_regions = [
        (-10, 40),  # Western Mediterranean (Spain, Portugal)
        (10, 30),   # Central Mediterranean (Italy, Greece)
        (30, 40)    # Eastern Mediterranean (Turkey)
    ]
    return any(lower <= longitude <= upper for lower, upper in mediterranean_regions)


def _estimate_budget_range(budget):
    """
    Estimate budget range based on place details and ratings
    """
    budget = int(budget)
    if budget > 80000:
        return 'luxury'
    elif budget > 30000:
        return 'high'
    elif budget > 10000:
        return 'medium'
    else:
        return 'low'
    
# Plan a Trip View
@login_required
def plan_trip(request):
    if request.method == 'POST':
        try:
            destination_name = request.POST['destination']
            budget = request.POST.get('budget', None)
            
            # Attempt to enrich destination details
            destination_info = enrich_destination_details(destination_name, budget)
            
            destination_defaults = {
                'country': destination_info.get('country', 'Unknown'),
                'climate': destination_info.get('climate', 'temperate'),
                'category': destination_info.get('types', ['city'])[0], 
                'budget_range': destination_info.get('budget_range', 'medium'),
                'latitude': destination_info.get('latitude', 0),
                'longitude': destination_info.get('longitude', 0),
            }
            
            destination, created = Destination.objects.get_or_create(
                name=destination_name,
                defaults=destination_defaults
            )

            start_date = parse_date(request.POST['start_date'])
            end_date = parse_date(request.POST['end_date'])
            if not start_date or not end_date:
                raise ValidationError("Start and End dates are required.")

            if start_date > end_date:
                raise ValidationError("Start date cannot be later than end date.")
            
            # Create a new trip with the submitted data 
            activities = request.POST['activities']
            accommodation = request.POST['accommodation']
            transportation = request.POST['transportation']
            budget = request.POST.get('budget', None) 
            packing_list = request.POST['packing_list']
            travel_notes = request.POST['travel_notes']

            trip = Trip(
                user=request.user,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                activities=activities,
                accommodation=accommodation,
                transportation=transportation,
                budget=budget,
                packing_list=packing_list,
                travel_notes=travel_notes,
            )
            trip.save()
            messages.success(request, 'Trip planned successfully!')
            return redirect('my_trips')

        except ValidationError as e:
            messages.error(request, str(e))

    #destinations = Destination.objects.all()
    return render(request, 'plan_trip.html')

@login_required
def trip_edit(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if request.method == 'POST':
        # Update the trip with submitted data
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Validate dates
        if not start_date or not end_date:
            messages.error(request, 'Start and end dates are required.')
            return render(request, 'trip_edit.html', {'trip': trip})

        trip.start_date = start_date
        trip.end_date = end_date
        trip.activities = request.POST.get('activities')
        trip.accommodation = request.POST.get('accommodation')
        trip.transportation = request.POST.get('transportation')
        trip.budget = request.POST.get('budget')
        trip.packing_list = request.POST.get('packing_list')
        trip.travel_notes = request.POST.get('travel_notes')
        
        # Save the updated trip back to the database
        trip.save()
        messages.success(request, 'Trip updated successfully.')
        return redirect('my_trips')  # Redirect to the trips list

    # Render the trip_edit template with the trip's current details
    return render(request, 'trip_edit.html', {'trip': trip})

@login_required
def trip_delete(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    trip.delete()
    messages.success(request, 'Trip deleted successfully.')
    return redirect('my_trips')

# Explore Destination View
@login_required
def explore_destination(request):
    #destinations = Destination.objects.all()
    return render(request, 'explore_destination.html')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Trip, Destination, RecommendationData
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pandas as pd

@login_required
def recommend_trip(request):
    try:
        # Get the user's profile and previous trips
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_trips = Trip.objects.filter(user=request.user)

        # Get destinations user has already visited
        visited_destinations = user_trips.values_list('destination__id', flat=True)

        # If no previous trips, suggest destinations based on profile
        if not user_trips.exists():
            recommendations = get_recommendations_for_new_user(user_profile)
            return process_recommendations(request, recommendations, user_profile)

        # Prepare data for machine learning
        trips_data = prepare_trip_data(user_trips)
        #print(trips_data)
        
        if len(trips_data) < 5:  # Not enough data for complex prediction
            recommendations = get_recommendations_for_new_user(user_profile)
            return process_recommendations(request, recommendations, user_profile)

        # Train recommendation model
        recommended_destinations = train_recommendation_model(trips_data, user_profile, visited_destinations)
        
        return process_recommendations(request, recommended_destinations, user_profile)
    
    except Exception as e:
        # More detailed error logging
        print(f"Recommendation Error: {e}")
        # Fallback to random recommendations
        recommendations = Destination.objects.order_by('?')[:5]
        return process_recommendations(request, recommendations, user_profile)

def process_recommendations(request, recommendations, user_profile):
    """
    Process and store recommendations
    """
    if recommendations:
        # Select the first recommendation
        recommended_destination = recommendations[0]
        #print(recommended_destination.name)
        
        # Check if recommendation already exists
        existing_recommendation = RecommendationData.objects.filter(
            user=request.user, 
            destination=recommended_destination
        ).first()
        
        # If no existing recommendation, create a new one
        if not existing_recommendation:
            RecommendationData.objects.create(
                user=request.user, 
                destination=recommended_destination,
            )
        
        return render(request, 'recommend_trip.html', {
            'destination': recommended_destination.name,
            'destination_obj': recommended_destination
        })
    else:
        return render(request, 'recommend_trip.html', {'destination': None})

def prepare_trip_data(user_trips):
    """
    Convert user trips to a structured DataFrame for ML
    """
    trips_data = []
    for trip in user_trips:
        trips_data.append({
            'Destination': trip.destination.name,
            'Country': trip.destination.country,
            'Climate': trip.destination.climate,
            'Category': trip.destination.category,
            'Budget_Range': trip.destination.budget_range,
            'Actual_Budget': trip.budget or 0,
        })
    return pd.DataFrame(trips_data)

def train_recommendation_model(trips_data, user_profile, visited_destinations):
    """
    Train a machine learning model to recommend destinations
    """
    # Prepare features
    X = trips_data.drop('Destination', axis=1)
    y = trips_data['Destination']

    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), # One-hot encode categorical features
             ['Country', 'Climate', 'Category', 'Budget_Range']),
            ('num', 'passthrough', ['Actual_Budget']) # Pass through numerical features without changes
        ])

    # Create pipeline
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)) # 100 trees and fixed random seed for reproducibility
    ])

    # Train the model
    model.fit(X, y)

    # Prepare new trip features based on user profile
    new_trip_features = pd.DataFrame([{
        'Country': user_profile.location or 'Unknown',
        'Climate': user_profile.preferred_climate or trips_data['Climate'].mode()[0], # Use mode for taking most common value
        'Category': user_profile.preferred_category or trips_data['Category'].mode()[0],
        'Budget_Range': user_profile.preferred_budget_range or trips_data['Budget_Range'].mode()[0],
        'Actual_Budget': trips_data['Actual_Budget'].mean() # Use average budget for new trip
    }])

    # Predict new destinations based on user profile and previous trips
    predicted_destinations = model.predict(new_trip_features)
    
    # Get recommended destinations, excluding already visited
    recommendations = Destination.objects.filter(
        name__in=predicted_destinations
    ).exclude(id__in=visited_destinations) 
    
    # If no recommendations, fall back to profile-based recommendations
    if not recommendations:
        recommendations = get_recommendations_for_new_user(user_profile)
    
    return recommendations

def get_recommendations_for_new_user(user_profile):
    """
    Generate recommendations for users with no trip history, progressively relaxing preferences.
    """
    query = Destination.objects.all()

    # Filter by all 3 preferences
    recommendations = query.filter(
        climate=user_profile.preferred_climate,
        category=user_profile.preferred_category,
        budget_range=user_profile.preferred_budget_range
    )
    
    if recommendations.exists():
        return recommendations.order_by('?')[:5]  # Return top 5 random matches

    # Filter by 2 preferences: Climate and Category
    recommendations = query.filter(
        climate=user_profile.preferred_climate,
        category=user_profile.preferred_category
    )
    
    if recommendations.exists():
        return recommendations.order_by('?')[:5]

    # Filter by 2 preferences: Climate and Budget Range
    recommendations = query.filter(
        climate=user_profile.preferred_climate,
        budget_range=user_profile.preferred_budget_range
    )
    
    if recommendations.exists():
        return recommendations.order_by('?')[:5]

    # Filter by 2 preferences: Category and Budget Range
    recommendations = query.filter(
        category=user_profile.preferred_category,
        budget_range=user_profile.preferred_budget_range
    )
    
    if recommendations.exists():
        return recommendations.order_by('?')[:5]

    # Filter by 1 preference: Climate
    recommendations = query.filter(climate=user_profile.preferred_climate)
    if recommendations.exists():
        return recommendations.order_by('?')[:5]

    # Filter by 1 preference: Category
    recommendations = query.filter(category=user_profile.preferred_category)
    if recommendations.exists():
        return recommendations.order_by('?')[:5]

    # Filter by 1 preference: Budget Range
    recommendations = query.filter(budget_range=user_profile.preferred_budget_range)
    if recommendations.exists():
        return recommendations.order_by('?')[:5]

    # If no preferences match, return random destinations
    return Destination.objects.order_by('?')[:5]