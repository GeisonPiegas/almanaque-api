from src.apps.users.models import Users


def get_user(id: str):
    instance = Users.objects.filter(external_id=id).first()

    if instance:
        return instance
    else:
        instance = Users.objects.create(
            name="Usuário",
            external_id=id,
        )
        return instance
