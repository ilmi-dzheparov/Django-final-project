from django.shortcuts import render
from django.views.generic import ListView
from models import Category, Product
from django.core.cache import cache
from django.conf import settings


class ProductListView(ListView):
    template_name = "product/catalog.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        cache_key = 'categories'
        categories = cache.get(cache_key)
        if categories is None:
            categories = Category.objects.filter(products__available=True).prefetch_related('products')

            context[cache_key] = categories
            cache.set(cache_key, categories, settings.DEFAULT_CACHE_TIME)
        else:
            context[cache_key] = categories

        context['products'] = Product.objects.all().select_related('category')

        return context
