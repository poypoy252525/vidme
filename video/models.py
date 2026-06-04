from django.db import models

# Create your models here.

class Video(models.Model):
    title = models.CharField()
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='videos/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

