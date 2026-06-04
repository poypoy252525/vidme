from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from .models import Video


@shared_task(bind=True, name='video.convert_uploaded_video')
def convert_uploaded_video_task(self, video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except ObjectDoesNotExist:
        return None

    video.convert_uploaded_video()
    return video_id
