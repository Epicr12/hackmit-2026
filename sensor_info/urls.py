from django.urls import path
from . import views

urlpatterns = [
    path("", views.sensor_page, name="sensors"),
]
