from django.shortcuts import render
from src.banners.models import Banner
from django.views.decorators.cache import cache_page


@cache_page(600)  # кэширование баннера на 10 минут
def random_banners_view(request):
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

    return render(request, "banner.html", context)

