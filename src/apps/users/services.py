from src.apps.users.models import Users


def get_user(id: str, name: str | None = None, email: str | None = None, avatar_url: str | None = None):
    instance, _ = Users.objects.get_or_create(
        external_id=id,
        defaults={
            "name": name,
            "email": email,
            "avatar_url": avatar_url,
        },
    )
    return instance
