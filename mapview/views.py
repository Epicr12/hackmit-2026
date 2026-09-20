from django.http import JsonResponse

from django.shortcuts import render

from .models import CountyImpact, Stream

# The sensor network reads total dissolved solids only.
READING_LABEL = "Dissolved solids"
READING_UNITS = "ppm"


def map_page(request):
    return render(request, "mapview/map.html", {
        "reading_label": READING_LABEL,
        "reading_units": READING_UNITS,
    })


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
    """Dissolved-solids readings for every stream, as a GeoJSON FeatureCollection."""
    features = []

    for stream in Stream.objects.all():
        if stream.tds_ppm is None:
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
                "label": READING_LABEL,
                "units": READING_UNITS,
                "value": stream.tds_ppm,
            },
        })

    return JsonResponse({"type": "FeatureCollection", "features": features})
