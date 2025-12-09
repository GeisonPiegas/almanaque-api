from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from src.apps.posts.services import recalculate_user_preferences_embedding

from .models import Reactions

# @receiver(post_save, sender=Reactions)
# def update_user_keyword_preferences_on_reaction(sender, instance, created, **kwargs):
#     """
#     Toda vez que o user reagir a um post, atualiza o score das keywords desse post
#     para aquele user.
#     """
#     weight = 0

#     if created:
#         weight = REACTION_WEIGHTS.get(instance.type, 0)
#     else:
#         old_type = getattr(instance, "_old_type", None)
#         old_weight = REACTION_WEIGHTS.get(old_type, 0)
#         new_weight = REACTION_WEIGHTS.get(instance.type, 0)
#         weight = new_weight - old_weight

#     if weight == 0:
#         return

#     keywords = instance.post.keywords.all()
#     for keyword in keywords:
#         pref, _ = UserKeywordPreference.objects.get_or_create(
#             user=instance.user,
#             keyword=keyword,
#             defaults={"score": 0},
#         )
#         UserKeywordPreference.objects.filter(pk=pref.pk).update(score=F("score") + weight)


# @receiver(post_delete, sender=Reactions)
# def decrease_user_keyword_preferences_on_reaction_delete(sender, instance, **kwargs):
#     """
#     Toda vez que o user deletar uma reação, atualiza o score das keywords desse post
#     para aquele user.
#     """
#     weight = REACTION_WEIGHTS.get(instance.type, 0)

#     if weight == 0:
#         return

#     keywords = instance.post.keywords.all()
#     for keyword in keywords:
#         UserKeywordPreference.objects.filter(
#             user=instance.user,
#             keyword=keyword,
#         ).update(score=F("score") + weight)


@receiver(post_save, sender=Reactions)
def update_user_embedding_on_reaction_save(sender, instance: Reactions, **kwargs):
    recalculate_user_preferences_embedding(instance.user)


@receiver(post_delete, sender=Reactions)
def update_user_embedding_on_reaction_delete(sender, instance: Reactions, **kwargs):
    recalculate_user_preferences_embedding(instance.user)


# from django.db.models import Sum
# from .models import Posts
#
# def get_recommended_posts_for_user(user, limit=20):
#     """
#     Retorna posts ordenados pelo 'interesse' do usuário,
#     baseado nas keywords com score positivo.
#     """
#     qs = (
#         Posts.objects
#         # só posts com keywords que o user tem preferência
#         .filter(keywords__user_preferences__user=user,
#                 keywords__user_preferences__score__gt=0)
#         # não recomendar posts que o user já reagiu
#         .exclude(reactions__user=user)
#         # score = soma do score das keywords do post para aquele user
#         .annotate(
#             interest_score=Sum('keywords__user_preferences__score')
#         )
#         .order_by('-interest_score', '-created_at')
#         .distinct()
#     )

#     return qs[:limit]
