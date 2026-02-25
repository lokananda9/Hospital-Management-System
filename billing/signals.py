from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Invoice


@receiver(post_save, sender=Invoice)
@receiver(post_delete, sender=Invoice)
def invalidate_dashboard_cache(*args, **kwargs):
    cache.delete("dashboard_overview")
