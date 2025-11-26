import re

import instaloader
import requests


class InstagramAPI:
    def __init__(self):
        self.L = instaloader.Instaloader()

    def extract_shortcode_from_url(self, reels_url: str) -> str:
        """
        Extrai o shortcode da URL de um Reels.
        Ex: https://www.instagram.com/reel/DRIQpt6DiF3/ -> DRIQpt6DiF3
        """
        match = re.search(r"/reel/([^/?]+)/?", reels_url)
        if not match:
            raise ValueError(f"URL de Reels inválida: {reels_url}")
        return match.group(1)

    def get_reels_data(self, reels_url: str) -> dict[str, any]:
        """
        Recebe a URL de um Reels público e retorna:
        - Metadados (caption, usuário, data, likes, comments…)
        - URL da thumbnail
        - URL do vídeo (se for Reels de vídeo)
        """

        # Cria o contexto do Instaloader
        L = self.L

        # Se precisar acessar privados, dá pra fazer login:
        L.login("geison_piegas", "piegas753")

        shortcode = self.extract_shortcode_from_url(reels_url)

        # Carrega o post a partir do shortcode
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Monta um dicionário com os dados mais úteis
        data: dict[str, any] = {
            "shortcode": post.shortcode,  # ex: DRIQpt6DiF3
            "media_id": post.mediaid,  # id numérico interno
            "is_video": post.is_video,  # True para Reels
            "owner_username": post.owner_username,  # @dono_do_post
            "caption": post.caption,  # legenda completa
            "taken_at_utc": post.date_utc.isoformat(),  # datetime -> string ISO
            "taken_at_local": post.date_local.isoformat(),
            "likes": post.likes,
            "comments_count": post.comments,
            "thumbnail_url": post.url,  # thumbnail (imagem)
            "video_url": post.video_url,  # url do .mp4 se for vídeo
            "permalink": f"https://www.instagram.com/reel/{post.shortcode}/",
            "hashtags": post.caption_hashtags,
            "mentions": post.caption_mentions,
        }

        return data

    def download_reels_media_if_video(self, data: dict[str, any], output_path: str) -> None:
        """
        Faz o download do vídeo do Reels para um arquivo local, se for vídeo.
        """
        if not data.get("is_video"):
            print("Este Reels não é um vídeo (provavelmente imagem/carrossel).")
            return

        video_url = data.get("video_url")
        if not video_url:
            print("Não foi possível obter a URL do vídeo.")
            return

        resp = requests.get(video_url, stream=True, timeout=30)
        resp.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"Vídeo salvo em: {output_path}")

    def exec(self, url: str, output_path: str):
        data = self.get_reels_data(url)
        # self.download_reels_media_if_video(data, output_path)
        return data
