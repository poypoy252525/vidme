import os
import subprocess
from django.conf import settings
from django.db import models

# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='videos/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_file_name = self.file.name if self.file else None

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        file_changed = bool(self.file and self.file.name != self._original_file_name)

        super().save(*args, **kwargs)

        if is_new or file_changed:
            from .tasks import convert_uploaded_video_task

            convert_uploaded_video_task.delay(self.pk)
            self._original_file_name = self.file.name

    def convert_uploaded_video(self):
        """
        Template method for converting or generating a processed video
        after a new file is uploaded or an existing file is replaced.

        Replace the placeholder steps below with your actual conversion logic.
        """
        if not self.file:
            return

        source_path = self.file.path
        base_name, _ = os.path.splitext(os.path.basename(source_path))
        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'converted')
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f"{base_name}_converted.mp4")

        # Example ffmpeg conversion command. Adjust codec, bitrate, and options as needed.
        ffmpeg_command = [
            'ffmpeg',
            '-i', source_path,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            output_path,
        ]

        try:
            subprocess.run(ffmpeg_command, check=True)
        except (OSError, subprocess.CalledProcessError):
            # If conversion fails, log or handle the failure as needed.
            return

        # At this point the converted file exists on disk.
        # Add any additional steps here, such as saving a reference to the
        # converted file in a separate model field or sending a notification.
        return output_path

