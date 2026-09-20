from django.urls import path
from . import views

urlpatterns = [
    path("", views.map_page, name="map"),

    path("sensor-data/", views.sensor_data, name="sensor_data.json"),
    path("county-impact/", views.county_impact, name="county_impact.json"),
]
