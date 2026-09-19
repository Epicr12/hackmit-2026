from django.urls import path
from . import views

urlpatterns = [
    path("", views.map_page, name="map"),
    """ change name later to sql """
    path("sensor-data/", views.sensor_data, name="sensor_data.json"),
]
