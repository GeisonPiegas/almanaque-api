import io
import os
import tempfile

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from moviepy import VideoFileClip
from PIL import Image


def generate_video_thumbnail_from_upload(
    uploaded_file: UploadedFile,
    timestamp: float = 0.5,
) -> ContentFile:
    """
    Gera uma thumbnail (JPEG) a partir de um UploadedFile de vídeo.
    Cria um arquivo temporário no disco (necessário pro ffmpeg/moviepy),
    pega um frame e devolve um ContentFile pronto pra ser salvo em um ImageField.
    """

    _, ext = os.path.splitext(uploaded_file.name)
    if not ext:
        ext = ".mp4"

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        for chunk in uploaded_file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    try:
        clip = VideoFileClip(tmp_path)

        ts = min(timestamp, max(0, clip.duration - 0.1))

        frame = clip.get_frame(ts)
        clip.close()
    finally:
        os.remove(tmp_path)

    image = Image.fromarray(frame)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)

    return ContentFile(buffer.getvalue(), name="thumbnail.jpg")
