from django.contrib import admin

from .models import CountyImpact, Stream


@admin.register(CountyImpact)
class CountyImpactAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "fips", "severity", "impaired_miles")
    list_filter = ("state",)
    search_fields = ("name", "fips")
    ordering = ("-severity",)


@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    list_display = ("name", "county_fips", "tds_ppm")
    search_fields = ("name",)
