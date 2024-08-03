from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from banners.models import Banner


# сигналы, позволяющие очищать кэш при изменении или удалении баннеров
@receiver(post_save, sender=Banner)
@receiver(post_delete, sender=Banner)
def reset_banners_cache(sender, **kwargs):
    cache.delete('banners')
