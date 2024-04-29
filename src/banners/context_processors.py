from .models import Banner


def random_banner_context_processor(request):
    """
        Добавляет в глобальный контекст три случайных баннера.
    """

    # Считаем сколько всего баннеров
    total_count = Banner.objects.filter(active=True).count()

    if total_count < 3:
        # Если меньше 3 активных, то выбираем все активные баннеры, что есть
        banners = Banner.objects.filter(active=True)
    else:
        # Иначе выбираем 3 случайных активных баннера
        banners = Banner.objects.filter(active=True).order_by("?")[:3]

    context = {
        "banners": banners,
    }

    return context
