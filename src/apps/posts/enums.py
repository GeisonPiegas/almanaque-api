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
    DISLIKE = "DISLIKE"
    LOVE = "LOVE"
    LAUGH = "LAUGH"
    WOW = "WOW"
    SAD = "SAD"
    ANGRY = "ANGRY"
    INSIGHTFUL = "INSIGHTFUL"


REACTION_TYPES = tuple((e.value, e.name) for e in ReactionTypes)


REACTION_WEIGHTS = {
    "LIKE": 1.0,
    "DISLIKE": -1.0,
    "LOVE": 2.0,
    "LAUGH": 1.5,
    "WOW": 1.5,
    "SAD": 0.3,
    "ANGRY": -1.0,
    "INSIGHTFUL": 1.0,
}
