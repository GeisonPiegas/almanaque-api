from enum import IntEnum


class MemeType(IntEnum):
    IMAGE = 1
    GIF = 2
    VIDEO = 3


MEME_TYPE = tuple((e.value, e.name) for e in MemeType)


class MemeStatus(IntEnum):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3


MEME_STATUS = tuple((e.value, e.name) for e in MemeStatus)
