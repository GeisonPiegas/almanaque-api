import math

from src.apps.posts.enums import REACTION_WEIGHTS
from src.apps.users.models import Users

from .models import Reactions


def _weighted_mean_normalized(vectors: list[list[float]], weights: list[float]) -> list[float] | None:
    if not vectors:
        return None

    dimensions = len(vectors[0])
    agg = [0.0] * dimensions
    total_weight = 0.0

    for vector, weight in zip(vectors, weights):
        if weight == 0:
            continue
        total_weight += abs(weight)
        for dimension in range(dimensions):
            agg[dimension] += weight * vector[dimension]

    if total_weight == 0:
        return None

    # média ponderada
    avg = [v / total_weight for v in agg]

    # normaliza (norma 1.0)
    normalize = math.sqrt(sum(x * x for x in avg))
    if normalize == 0:
        return None

    return [x / normalize for x in avg]


def recalculate_user_preferences_embedding(user: Users) -> None:
    reactions = Reactions.objects.select_related("post").filter(user=user).exclude(post__embedding=None)

    if not reactions.exists():
        user.preferences_embedding = None
        user.save(update_fields=["preferences_embedding"])
        return

    vectors: list[list[float]] = []
    weights: list[float] = []

    for reaction in reactions:
        weight = REACTION_WEIGHTS.get(reaction.type, 0.0)
        if weight == 0:
            continue

        embedding = reaction.post.embedding
        if not list(embedding):
            continue

        vectors.append(list(embedding))
        weights.append(weight)

    user_vector = _weighted_mean_normalized(vectors, weights)

    user.preferences_embedding = user_vector
    user.save(update_fields=["preferences_embedding"])
