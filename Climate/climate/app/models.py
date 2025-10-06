from django.db import models

class Dataset(models.Model):
    SOURCE_CHOICES = [
        ("Satellite", "Satellite"),
        ("Sensor", "Sensor"),
        ("Weather Station", "Weather Station"),
        ("Historical Data", "Historical Data"),
    ]

    FORMAT_CHOICES = [
        ("CSV", "CSV"),
        ("JSON", "JSON"),
        ("NetCDF", "NetCDF"),
        ("Image", "Image"),
        ("Other", "Other"),
    ]

    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    file_format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    upload_file = models.FileField(upload_to="datasets/", blank=True, null=True)
    data_source_url = models.URLField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_real_time = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
