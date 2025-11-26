import io
from os import name

from django.core.files.base import ContentFile
from moviepy import VideoFileClip
from PIL import Image


def generate_video_thumbnail(video_path: str, timestamp: float = 0.5) -> ContentFile:
    """
    Gera uma thumbnail (JPEG) a partir de um vídeo em `video_path`.
    `timestamp` é em segundos (0.5 = meio segundo de vídeo).
    Retorna um ContentFile pronto pra ser usado em um ImageField.
    """
    clip = VideoFileClip(video_path)

    # Garante que o timestamp existe dentro da duração do vídeo
    ts = min(timestamp, max(0, clip.duration - 0.1))

    # Pega o frame como np.array
    frame = clip.get_frame(ts)
    clip.close()

    # Converte para imagem PIL
    image = Image.fromarray(frame)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)

    # O nome real você define na hora de salvar no campo do model
    return ContentFile(buffer.getvalue(), name="thumbnail.jpg")
