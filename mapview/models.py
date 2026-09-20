from django.db import models

class Stream(models.Model):
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()

    ph = models.FloatField(null=True, blank=True)
    """temperature = models.FloatField(null=True, blank=True)
    dissolved_oxygen = models.FloatField(null=True, blank=True)
    turbidity = models.FloatField(null=True, blank=True)"""

    def __str__(self):
        return self.name

    