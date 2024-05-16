from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from shop.models import Category, Product, SellerProduct


@receiver(signal=post_save, sender=Category)
@receiver(signal=post_delete, sender=Category)
def clear_menu_cache(sender, **kwargs):
    cache.delete('categories')


@receiver(post_save, sender=Product)
def reset_cache(sender, instance, **kwargs):
    cache.delete('product_cache_key')


@receiver(post_save, sender=SellerProduct)
@receiver(post_delete, sender=SellerProduct)
def clear_product_cache(sender, **kwargs):
    keys = cache.keys('products-*')
    for key in keys:
        cache.delete(key)
