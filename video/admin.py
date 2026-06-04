from django.contrib import admin

from video.models import Video


# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')