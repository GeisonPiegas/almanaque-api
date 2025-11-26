import os


def path_and_rename_media(object, filename):
    upload_to = type(object).__name__.lower()
    ext = filename.split(".")[-1]
    filename = f"{str(object.uuid)}/media.{ext}"
    return os.path.join(upload_to, filename)


def path_and_rename_thumbnail(object, filename):
    upload_to = type(object).__name__.lower()
    ext = filename.split(".")[-1]
    filename = f"{str(object.uuid)}/thumbnail.{ext}"
    return os.path.join(upload_to, filename)
