from .models import Banner


def random_banner_context_processor(request):
    """
        Добавляет в глобальный контекст три случайных баннера.
    """

    # Считаем сколько всего баннеров
    total_count = Banner.objects.count()

    if total_count < 3:
        # Если меньше 3, то выбираем все, что есть
        banners = Banner.objects.all()
    else:
        # Иначе выбираем 3 случайных баннера
        banners = Banner.objects.filter(active=True).order_by("?")[:3]

    context = {
        "banners": banners,
    }

    return context
