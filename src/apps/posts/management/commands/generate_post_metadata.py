import uuid

from django.core.management.base import BaseCommand

from src.apps.posts.models import Posts
from src.integrations.almanaque_ai import AlmanaqueAI
from src.integrations.gemini import Gemini
from src.integrations.openai import OpenAI


class Command(BaseCommand):
    help = "Generate the image metadata for a specific POST."

    def add_arguments(self, parser):
        parser.add_argument("uuid", type=uuid.UUID, help="Post UUID")

    def handle(self, *args, **options):
        uuid = options["uuid"]
        instance = Posts.objects.filter(uuid=uuid).first()

        if not instance:
            raise ValueError(f"Post with UUID {uuid} not found.")

        almanaque_ai = AlmanaqueAI()
        self.stdout.write("Generating metadata for posts...")

        if not instance.description:
            raise ValueError("Post description is empty.")

        image_base64 = instance.media_to_base64()

        almanaque_metadata = almanaque_ai.process_image(image_base64)
        print(almanaque_metadata)

        openai = OpenAI()
        openai_metadata = openai.process_image(image_base64)
        print(openai_metadata)

        gemini = Gemini()
        gemini_metadata = gemini.process_image(image_base64)
        print(gemini_metadata)

        self.stdout.write(self.style.SUCCESS("Completed!"))
