from django.core.management.base import BaseCommand

from src.apps.posts.models import Posts
from src.integrations.openai import OpenAI


class Command(BaseCommand):
    help = "Generates embeddings for posts that don't already have embeddings."

    def handle(self, *args, **options):
        queryset = Posts.objects.filter(embedding__isnull=True)

        total = queryset.count()
        openai = OpenAI()
        self.stdout.write(f"Generating embeddings for {total} posts...")

        for post in queryset:
            if not post.description:
                continue

            embedding = openai.get_embedding(post.description)
            post.embedding = embedding
            post.save(update_fields=["embedding"])

        self.stdout.write(self.style.SUCCESS("Completed!"))
