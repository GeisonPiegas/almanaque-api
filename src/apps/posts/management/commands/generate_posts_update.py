from django.core.management.base import BaseCommand

from src.apps.posts.models import Keywords, Posts
from src.integrations.almanaque_ai import AlmanaqueAI


class Command(BaseCommand):
    help = "Generates all data for posts."

    def handle(self, *args, **options):
        queryset = Posts.objects.all()

        total = queryset.count()
        almanaque_ai = AlmanaqueAI()
        self.stdout.write(f"Generating data for {total} posts...")

        for post in queryset:
            data = almanaque_ai.process_image(post.media_to_base64())

            keywords = []
            for keyword in data.get("keywords", []):
                _keyword, _ = Keywords.objects.get_or_create(name=keyword.upper())
                keywords.append(_keyword)

            post.title = data.get("title")
            post.description = data.get("description")
            if post.description:
                post.embedding = almanaque_ai.get_embedding(post.description)
            post.keywords.set(keywords)
            post.save()

        self.stdout.write(self.style.SUCCESS("Completed!"))
