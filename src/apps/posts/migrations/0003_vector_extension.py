from django.db import migrations
from pgvector.django import VectorExtension


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0002_favorites"),
    ]

    operations = [
        VectorExtension(),
    ]
