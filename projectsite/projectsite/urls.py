from django.contrib import admin
from django.urls import path
from fire.views import *
from fire import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-chart'),
    path('chart/', PieCountbySeverity, name='chart'),
    path('lineChart/', LineCountbyMonth, name='chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', multipleBarbySeverity, name='chart'),
    path('stations', views.map_station, name='map-station'),
    path('firestationlist', FireStationList.as_view(), name='firestation-list'),
    path('firestation/add', FireStationCreateView.as_view(), name='firestation-add'),
    path('firestationlist/<pk>', FireStationUpdateView.as_view(), name='firestation-update'),
    path('firestationlist/<pk>/delete', FireStationDeleteView.as_view(), name='firestation-delete'),

]