from rest_framework import serializers

from video.models import Video


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('id', 'title', 'description', 'file', 'stream_url', 'hls_manifest', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at', 'stream_url', 'hls_manifest')