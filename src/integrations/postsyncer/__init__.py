import requests


class Postsyncer:
    def __init__(self):
        self.base_url = "https://postsyncer.com/api/social-media-downloader"

    def get_social_media(self, url: str):
        payload = {"url": url, "platform": "all"}
        response = requests.post(self.base_url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("error", False):
                raise Exception(data.get("message", "Unknown error"))
            return data
        else:
            raise Exception(f"Failed to fetch data from {url}")
