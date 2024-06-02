from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from datetime import datetime
from django.shortcuts import render
from fire.models import Locations, Incident, FireStation, FireTruck, Firefighters, WeatherConditions
from fire.forms import FireStationForm, IncidentForm, LocationForm, FireTruckForm, FirefightersForm, WeatherConditionForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from django.views.generic.list import ListView
from django.db.models.query import QuerySet

class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass

def PieCountbySeverity(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    '''
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if rows:
        # Construct the dictionary with severity level as keys and count as values
        data = {severity: count for severity, count in rows}
    else:
        data = {}

    return JsonResponse(data)

def LineCountbyMonth(request):
    current_year = datetime.now().year
    result = {month: 0 for month in range(1, 13)}
    incidents_per_month = Incident.objects.filter(date_time__year=current_year) \
        .values_list('date_time', flat=True)
    # Counting the number of incidents per month
    for date_time in incidents_per_month:
        month = date_time.month
        result[month] += 1

    # If you want to convert month numbers to month names, you can use a dictionary mapping

    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    result_with_month_names = {
        month_names[int(month)]: count for month, count in result.items()}
    return JsonResponse(result_with_month_names)

def MultilineIncidentTop3Country(request):

    query = '''
        SELECT 
        fl.country,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN 
        fire_locations fl ON fi.location_id = fl.id
    WHERE 
        fl.country IN (
            SELECT 
                fl_top.country
            FROM 

                fire_incident fi_top
            JOIN 
                fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE 
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY 
                fl_top.country
            ORDER BY 
                COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY 
        fl.country, month
    ORDER BY 
        fl.country, month;
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Initialize a dictionary to store the result
    result = {}

    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}

        # Update the incident count for the corresponding month
        result[country][month] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        # Placeholder name for missing countries
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    for country in result:
        result[country] = dict(sorted(result[country].items()))
    return JsonResponse(result)

def multipleBarbySeverity(request):
    query = '''
    SELECT 
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    GROUP BY fi.severity_level, month
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        level = str(row[0])  # Ensure the severity level is a string
        month = row[1]
        total_incidents = row[2]
        if level not in result:
            result[level] = {month: 0 for month in months}
        result[level][month] = total_incidents

    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)

def map_station(request):
     fireStations = FireStation.objects.values('name', 'latitude', 'longitude', 'city', 'address')

     for fs in fireStations:
         fs['latitude'] = float(fs['latitude'])
         fs['longitude'] = float(fs['longitude'])

     fireStations_list = list(fireStations)

     cities = FireStation.objects.values_list('city', flat=True).distinct()

     context = {
         'fireStations': fireStations_list,
         'cities': cities,
     }

     return render(request, 'map_station.html', context)

def map_incident(request):
    incidents = Incident.objects.select_related('location').all()
    incident_data = []
    cities = set()

    for incident in incidents:
        incident_data.append({
            'id': incident.id,
            'description': incident.description,
            'severity_level': incident.severity_level,
            'date_time': incident.date_time.strftime('%Y-%m-%d %H:%M:%S') if incident.date_time else '',
            'latitude': float(incident.location.latitude),
            'longitude': float(incident.location.longitude),
            'address': incident.location.address,
            'city': incident.location.city,
        })
        cities.add(incident.location.city)

    return render(request, 'map_incident.html', {'incidentData': incident_data, 'cities': list(cities)})

class FireStationList(ListView):
    model = FireStation
    context_object_name = 'firestation'
    template_name = "listfirestations.html"
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(FireStationList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
            Q(city__icontains=query) | Q(country__icontains=query))
        return qs

class FireStationCreateView(CreateView):
    model = FireStation
    form_class = FireStationForm
    template_name = "addfirestations.html"
    success_url = reverse_lazy('firestation-add')

class FireStationUpdateView(UpdateView):
    model = FireStation
    form_class = FireStationForm
    template_name = "editfirestations.html"
    success_url = reverse_lazy('firestation-update')

class FireStationDeleteView(DeleteView):
    model = FireStation
    template_name = 'delfirestations.html'
    success_url = reverse_lazy('firestation-delete')

class FireFighterList(ListView):
    model = Firefighters
    context_object_name = 'firefighters'
    template_name = "listfirefighters.html"
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(FireFighterList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
            Q(rank__icontains=query) | Q(experience_level__icontains=query) | Q(station__icontains=query))
        return qs

class FireFighterCreateView(CreateView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = "addfirefighter.html"
    success_url = reverse_lazy('firefighter-add')

class FireFighterUpdateView(UpdateView):
    model = Firefighters
    form_class = FirefightersForm
    template_name = "editfirefighter.html"
    success_url = reverse_lazy('firefighter-update')

class FireFighterDeleteView(DeleteView):
    model = Firefighters
    template_name = 'delfirefighter.html'
    success_url = reverse_lazy('firefighter-delete')

class IncidentList(ListView):
    model = Incident
    context_object_name = 'incident'
    template_name = "listincident.html"
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(IncidentList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(location__name__icontains=query) |
            Q(date_time__icontains=query) | Q(severity_level__icontains=query))
        return qs

class IncidentCreateView(CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = "addincident.html"
    success_url = reverse_lazy('incident-add')

class IncidentUpdateView(UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = "editincident.html"
    success_url = reverse_lazy('incident-update')

class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = 'delincident.html'
    success_url = reverse_lazy('incident-delete')

class LocationList(ListView):
    model = Locations
    context_object_name = 'locations'
    template_name = "listloc.html"
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(LocationList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) |
            Q(city__icontains=query) | Q(country__icontains=query))
        return qs

class LocationCreateView(CreateView):
    model = Locations
    form_class = LocationForm
    template_name = "addloc.html"
    success_url = reverse_lazy('location-add')

class LocationUpdateView(UpdateView):
    model = Locations
    form_class = LocationForm
    template_name = "editloc.html"
    success_url = reverse_lazy('ocation-update')

class LocationDeleteView(DeleteView):
    model = Locations
    template_name = 'delloc.html'
    success_url = reverse_lazy('location-delete')


class FireTruckList(ListView):
    model = FireTruck
    context_object_name = 'firetruck'
    template_name = "listtruck.html"
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(FireTruckList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(truck_number__icontains=query) |
            Q(model__icontains=query) | Q(capacity__icontains=query) | Q(station__name__icontains=query))
        return qs

class FireTruckCreateView(CreateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = "addtruck.html"
    success_url = reverse_lazy('weathercondition-add')

class FireTruckUpdateView(UpdateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = "edittruck.html"
    success_url = reverse_lazy('weathercondition-update')

class FireTruckDeleteView(DeleteView):
    model = FireTruck
    template_name = 'deltruck.html'
    success_url = reverse_lazy('weathercondition-delete')

class WeatherConditionList(ListView):
    model = WeatherConditions
    context_object_name = 'weathercondition'
    template_name = "listwea.html"
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super(WeatherConditionList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(incident__description__icontains=query) |
            Q(temperature__icontains=query) | Q(humidity__icontains=query) | Q(wind_speed__icontains=query))
        return qs

class WeatherConditionCreateView(CreateView):
    model = WeatherConditions
    form_class = WeatherConditionForm
    template_name = "addwea.html"
    success_url = reverse_lazy('firetruck-add')

class WeatherConditionUpdateView(UpdateView):
    model = WeatherConditions
    form_class = WeatherConditionForm
    template_name = "editwea.html"
    success_url = reverse_lazy('firetruck-update')

class WeatherConditionDeleteView(DeleteView):
    model = WeatherConditions
    template_name = 'delwea.html'
    success_url = reverse_lazy('firetruck-delete')