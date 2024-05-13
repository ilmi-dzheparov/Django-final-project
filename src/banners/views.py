from django.shortcuts import render
from src.banners.models import Banner
from django.core.cache import cache
from django.views.generic import ListView


class BannerListView(ListView):

    def random_banners(self, request):
        """
        Добавляет в глобальный контекст три случайных баннера.
        """

        if 'banners' in cache:
            # Если баннеры уже находятся в кэше, используем их
            banners = cache.get('banners')
        else:
            # Считаем сколько всего баннеров
            total_count = Banner.objects.filter(active=True).count()

            if total_count < 3:
                # Если меньше 3 активных, то выбираем все активные баннеры, что есть
                banners = Banner.objects.filter(active=True)
            else:
                # Иначе выбираем 3 случайных активных баннера
                banners = Banner.objects.filter(active=True).order_by("?")[:3]

        # Сохраняем баннеры в кэше
        cache.set('banners', banners, 600)  # кэширование на 10 минут

        context = {
            "banners": banners,
        }

        return render(request, "banner.html", context)
