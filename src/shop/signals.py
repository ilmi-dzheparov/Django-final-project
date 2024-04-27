from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Category


@receiver(signal=post_save, sender=Category)
@receiver(signal=post_delete, sender=Category)
def clear_menu_cache(sender, **kwargs):
    cache.delete('categories')
