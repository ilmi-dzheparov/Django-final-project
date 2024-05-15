from django.core.cache import cache
from django.conf import settings
from .models import Category, SellerProduct


def get_cached_categories():
    cache_key = 'categories'
    categories = cache.get(cache_key)
    if categories is None:
        categories = Category.objects.filter(products__available=True).prefetch_related('products')
        cache.set(cache_key, categories, settings.DEFAULT_CACHE_TIME)
    return categories


def get_cached_products(tag, sort):
    cache_key = f'products-{sort}-{tag}'
    products = cache.get(cache_key)
    if products is None:

        products = SellerProduct.objects.all()

        if sort == 'price':
            products = products.order_by('price')
        if sort == 'review':
            products = products.product.order_by('-reviews')
        if sort == 'newness':
            products = products.order_by('created_at')
        if sort == 'popularity:':
            products = products.order_by('-popularity')

        if tag:
            products = products.filter(tags__name=tag)

        cache.set(cache_key, products, settings.DEFAULT_CACHE_TIME)

    return products
