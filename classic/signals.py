from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import DailyActivity


@receiver(pre_save, sender=DailyActivity)
def remember_previous_adventures(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_adventures = 0
        return
    previous = sender.objects.filter(pk=instance.pk).values_list("adventures", flat=True).first()
    instance._previous_adventures = previous or 0


@receiver(post_save, sender=DailyActivity)
def recruit_colony_from_adventures(sender, instance, created, **kwargs):
    previous = getattr(instance, "_previous_adventures", 0)
    gained = max(0, instance.adventures - previous)
    if not gained:
        return
    from .colony import recruit_inhabitants

    recruit_inhabitants(instance.character, gained)
