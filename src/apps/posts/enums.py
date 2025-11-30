from enum import StrEnum


class PostTypes(StrEnum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


POST_TYPES = tuple((e.value, e.name) for e in PostTypes)


class PostStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


POST_STATUS = tuple((e.value, e.name) for e in PostStatus)


class ReactionTypes(StrEnum):
    LIKE = "LIKE"
    LOVE = "LOVE"
    LAUGH = "LAUGH"
    WOW = "WOW"
    SAD = "SAD"
    ANGRY = "ANGRY"
    INSIGHTFUL = "INSIGHTFUL"


REACTION_TYPES = tuple((e.value, e.name) for e in ReactionTypes)
