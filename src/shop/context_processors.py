from .services import get_cached_categories, get_cached_products


def categories(request):
    return {'categories': get_cached_categories()}


def products(request, tag, sort):
    return {f'products-{sort}-{tag}': get_cached_products(tag, sort)}
