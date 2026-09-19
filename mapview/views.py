from django.shortcuts import render
from django.http import JsonResponse

from .models import Stream

def map_page(request):
    return render(request, "mapview/map.html")

def sensor_data(request):
    
    """returns SQL column"""
    """IF sql formatting follows"""
    sensor = request.GET.get("sensor", "ph") 

    streams = Stream.objects.all()

    data = []