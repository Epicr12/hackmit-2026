from django.db import models


class Stream(models.Model):
    """A stream monitoring point with its latest sensor reading."""

    name = models.CharField(max_length=200)
    county_fips = models.CharField(max_length=5, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    # The sensors read total dissolved solids only, in parts per million.
    tds_ppm = models.FloatField(
        null=True, blank=True,
        verbose_name="dissolved solids (ppm)",
        help_text="Total dissolved solids in parts per million",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CountyImpact(models.Model):
    """AMD damage intensity for one county, as a 0-100 index.

    The seed data shipped in mapview/fixtures/amd_seed.json is an illustrative
    index built from the documented AMD-affected watersheds, not a regulatory
    dataset. Replace the fixture (or edit rows in the admin) when real numbers
    are available -- nothing else needs to change.
    """

    fips = models.CharField(max_length=5, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    severity = models.FloatField(help_text="0-100 AMD damage intensity index")
    impaired_miles = models.FloatField(null=True, blank=True)
    basis = models.TextField(blank=True, help_text="Watersheds this score is based on")

    class Meta:
        ordering = ["-severity", "name"]

    def __str__(self):
        return f"{self.name}, {self.state} ({self.severity:.0f})"
