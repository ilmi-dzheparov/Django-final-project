from django.shortcuts import render
from banners.models import Banner
from django.core.cache import cache
from django.views.generic import ListView


class BannerListView(ListView):

    def random_banners(self, request):
        """
        Добавляет в глобальный контекст три случайных баннера.
        """

        if 'banners' in cache:
            banners = cache.get('banners')
        else:
            total_count = Banner.objects.filter(active=True).count()

            if total_count < 3:
                banners = Banner.objects.filter(active=True)
            else:
                banners = Banner.objects.filter(active=True).order_by("?")[:3]

        cache.set('banners', banners, 600)

        context = {
            "banners": banners,
        }

        return render(request, "banners/banner.html", context)
