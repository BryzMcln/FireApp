from django.forms import ModelForm, DateTimeInput
from django import forms
from fire.models import Locations, Incident, FireStation, FireTruck, Firefighters, WeatherConditions

class FireStationForm(ModelForm):
    class Meta:
        model = FireStation
        fields = "__all__"
        labels = {
            'name': 'Fire Station Name',  
            'latitude': 'Latitude',  
            'longitude': 'Longitude',
            'address': 'Address',
            'city': 'City',
            'country': 'Country',
        }


class IncidentForm(ModelForm):
    date_time = forms.DateTimeField(
        widget=DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',  # You can add any class you need for styling
            'placeholder': 'Select Date and Time',
        })
    )
    class Meta:
        model = Incident
        fields = "__all__"
        labels = {
            'location': 'Location',  
            'date_time': 'Date Time',  
            'severity_level': 'Severity Level',
            'description': 'Description',
        }

class LocationForm(ModelForm):
    class Meta:
        model = Locations
        fields = "__all__"
        labels = {
            'name': 'Location Name',  
            'latitude': 'Latitude',  
            'longitude': 'Longitude',
            'address': 'Address',
            'city': 'City',
            'country': 'Country',
        }

class FireTruckForm(ModelForm):
    class Meta:
        model = FireTruck
        fields = "__all__"
        labels = {
            'truck_number': 'Truck Number',  
            'model': 'Model',  
            'capacity': 'Capacity',
            'station': 'Station',
        }


class FirefightersForm(ModelForm):
    class Meta:
        model = Firefighters
        fields = "__all__"
        labels = {
            'name': 'Name',  
            'rank': 'Rank',  
            'experience_level': 'Experience Level',
            'station': 'Station',
        }

class WeatherConditionForm(ModelForm):
    class Meta:
        model = WeatherConditions
        fields = "__all__"
        labels = {
            'incident': 'Incident',  
            'temperature': 'Temperature',  
            'humidity': 'Humidity',
            'wind_speed': 'Wind Speed',
            'weather_description': 'Weather Description',
        }