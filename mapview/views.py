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

    for stream in streams:

        if sensor == "ph":
            value = stream.ph

        elif sensor == "temperature":
            value = stream.temperature

        elif sensor == "dissolved_oxygen":
            value = stream.dissolved_oxygen

        elif sensor == "turbidity":
            value = stream.turbidity

        else:
            value = None

        if value is not None:
            data.append({
                "name": stream.name,
                "latitude": stream.latitude,
                "longitude": stream.longitude,
                "value": value
            })

    return JsonResponse(data, safe=False)