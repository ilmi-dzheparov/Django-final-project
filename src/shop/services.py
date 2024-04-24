from django.core.cache import cache
from django.conf import settings
from .models import Category


def get_cached_categories():
    cache_key = 'categories'
    categories = cache.get(cache_key)
    if categories is None:
        categories = Category.objects.filter(products__available=True).prefetch_related('products')
        cache.set(cache_key, categories, settings.DEFAULT_CACHE_TIME)
    return categories
