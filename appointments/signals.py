from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Appointment


@receiver(post_save, sender=Appointment)
@receiver(post_delete, sender=Appointment)
def invalidate_dashboard_cache(*args, **kwargs):
    cache.delete("dashboard_overview")
