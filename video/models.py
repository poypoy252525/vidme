import logging
import os
import shutil
import subprocess
import tempfile
from django.conf import settings
from django.core.files import File
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

    def _get_source_file_path(self):
        if not self.file:
            return None, False

        storage = self.file.storage
        name = self.file.name

        if name and hasattr(storage, 'path'):
            try:
                return storage.path(name), False
            except (NotImplementedError, OSError):
                pass

        suffix = os.path.splitext(name)[1]
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        try:
            with storage.open(name, 'rb') as source, open(temp_file.name, 'wb') as dest:
                shutil.copyfileobj(source, dest)
        except Exception:
            os.unlink(temp_file.name)
            raise

        return temp_file.name, True

    def _upload_hls_assets(self, output_dir, manifest_name):
        storage = self.hls_manifest.storage
        manifest_path = os.path.join('videos', 'hls', manifest_name).replace('\\', '/')

        for root, _, files in os.walk(output_dir):
            for filename in files:
                local_path = os.path.join(root, filename)
                relative_path = os.path.relpath(local_path, output_dir)
                storage_path = os.path.join('videos', 'hls', relative_path).replace('\\', '/')

                if storage.exists(storage_path):
                    storage.delete(storage_path)
                with open(local_path, 'rb') as fh:
                    storage.save(storage_path, File(fh))

        self.hls_manifest.name = manifest_path
        self.save(update_fields=['hls_manifest'])

    def convert_uploaded_video(self):
        """
        Template method for converting or generating a processed video
        after a new file is uploaded or an existing file is replaced.

        Replace the placeholder steps below with your actual conversion logic.
        """
        if not self.file:
            return

        source_path, is_temp_source = self._get_source_file_path()
        if not source_path:
            raise RuntimeError("Unable to determine source file path for uploaded video.")

        try:
            base_name, _ = os.path.splitext(os.path.basename(source_path))
            manifest_name = f"{base_name}.m3u8"

            with tempfile.TemporaryDirectory() as temp_dir:
                output_dir = os.path.join(temp_dir, 'hls')
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
                    subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True)
                except FileNotFoundError as e:
                    raise RuntimeError(
                        f"FFmpeg executable not found at '{ffmpeg_path}'. Check your FFMPEG_PATH or system PATH."
                    ) from e
                except subprocess.CalledProcessError as e:
                    error_text = e.stderr or e.stdout or str(e)
                    raise RuntimeError(
                        f"FFmpeg failed generating HLS for {base_name}: {error_text}"
                    ) from e

                self._upload_hls_assets(output_dir, manifest_name)

            return manifest_path
        finally:
            if is_temp_source and source_path and os.path.exists(source_path):
                os.unlink(source_path)

