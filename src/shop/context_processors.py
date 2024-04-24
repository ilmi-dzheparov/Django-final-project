from .services import get_cached_categories


def categories(request):
    return {'categories': get_cached_categories()}
