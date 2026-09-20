from django.http import JsonResponse

from django.shortcuts import render

from .models import CountyImpact, Stream

# Sensors the map can colour by: field name -> (label, units).
# The <select> on the map page is built from this, so the two can't drift apart.
SENSORS = {
    "ph": ("pH", ""),
    "temperature": ("Temperature", "°C"),
    "dissolved_oxygen": ("Dissolved oxygen", "mg/L"),
    "turbidity": ("Turbidity", "NTU"),
}


def map_page(request):
    sensors = [
        {"key": key, "label": label, "units": units}
        for key, (label, units) in SENSORS.items()
    ]
    return render(request, "mapview/map.html", {"sensors": sensors})


def county_impact(request):
    """AMD damage intensity per county, keyed by 5-digit FIPS.

    Geometry is served separately as a static GeoJSON file and joined to this in
    the browser, so the boundaries stay cacheable and this payload stays small.
    """
    counties = {
        county.fips: {
            "name": county.name,
            "state": county.state,
            "severity": county.severity,
            "impaired_miles": county.impaired_miles,
            "basis": county.basis,
        }
        for county in CountyImpact.objects.all()
    }
    return JsonResponse({"counties": counties})


def sensor_data(request):
    """Stream readings for one sensor, as a GeoJSON FeatureCollection."""
    sensor = request.GET.get("sensor", "ph")

    if sensor not in SENSORS:
        return JsonResponse(
            {"error": f"unknown sensor {sensor!r}", "valid": sorted(SENSORS)},
            status=400,
        )

    label, units = SENSORS[sensor]

    features = []
    for stream in Stream.objects.all():
        value = getattr(stream, sensor)
        if value is None:
            continue
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [stream.longitude, stream.latitude],
            },
            "properties": {
                "name": stream.name,
                "county_fips": stream.county_fips,
                "sensor": sensor,
                "label": label,
                "units": units,
                "value": value,
            },
        })

    return JsonResponse({"type": "FeatureCollection", "features": features})
