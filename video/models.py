import logging
import os
import subprocess
from django.conf import settings
from django.db import models

# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='videos/')

    hls_manifest = models.FileField(upload_to='videos/hls/', blank=True, null=True)

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

        # Example ffmpeg HLS generation command.
        manifest_name = f"{base_name}.m3u8"
        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos', 'hls')
        os.makedirs(output_dir, exist_ok=True)

        manifest_path = os.path.join(output_dir, manifest_name)
        segment_pattern = os.path.join(output_dir, f"{base_name}_%03d.ts")

        ffmpeg_path = getattr(settings, 'FFMPEG_PATH', 'ffmpeg')
        ffmpeg_command = [
            ffmpeg_path,
            '-i', source_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-hls_time', '10',
            '-hls_playlist_type', 'vod',
            '-hls_segment_filename', segment_pattern,
            manifest_path,
        ]

        try:
            result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
        except FileNotFoundError as e:
            raise RuntimeError(
                f"FFmpeg executable not found at '{ffmpeg_path}'. Check your FFMPEG_PATH or system PATH."
            ) from e
        except subprocess.CalledProcessError as e:
            error_text = e.stderr or e.stdout or str(e)
            raise RuntimeError(
                f"FFmpeg failed generating HLS for {base_name}: {error_text}"
            ) from e

        # Save the manifest field once the HLS generation succeeds.
        self.hls_manifest.name = os.path.join('videos', 'hls', manifest_name).replace('\\', '/')
        self.save(update_fields=['hls_manifest'])

        return manifest_path

