import logging
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist

from .models import Video

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='video.convert_uploaded_video')
def convert_uploaded_video_task(self, video_id):
    try:
        video = Video.objects.get(pk=video_id)
    except ObjectDoesNotExist:
        logger.error(f"Video with id {video_id} not found")
        return None

    try:
        video.convert_uploaded_video()
        logger.info(f"Successfully generated HLS manifest for video {video_id}")
    except Exception as e:
        logger.error(f"Failed to convert video {video_id}: {str(e)}")
        raise
