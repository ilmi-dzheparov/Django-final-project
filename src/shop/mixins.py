from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


class NonCachingMixin:
    """
    Миксин 'NonCachingMixin' используется для предотвращения
    кеширования ответа представления, что гарантирует,
    что данные будут обновляться при каждом запросе
    """

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
