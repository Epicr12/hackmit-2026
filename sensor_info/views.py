from django.shortcuts import render


def sensor_page(request):
    return render(request, "sensor_info/sensors.html")
