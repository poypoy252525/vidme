from rest_framework import serializers

from video.models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('id', 'title', 'description', 'file', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')