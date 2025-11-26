from django.core.cache import cache
from storages.backends.gcloud import GoogleCloudStorage


class GoogleCloudMediaFileStorage(GoogleCloudStorage):
    def init(self, args, **kwargs):
        super().init(args, **kwargs)

    def url(self, name, *args, **kwargs):
        cache_key = f"signed_url_{name}"
        signed_url = cache.get(cache_key)
        if not signed_url:
            signed_url = super().url(name, *args, **kwargs)
            # Cache the signed URL with a timeout (e.g., 86400 seconds = 1 day)
            cache.set(cache_key, signed_url, timeout=86400)
        return signed_url
