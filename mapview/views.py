from django.shortcuts import render

def map_page(request):
    return render(request, "mapview/map.html")