from django.shortcuts import render
from django.views.generic import ListView
from models import Category, Product
from django.core.cache import cache


class ProductListView(ListView):
    template_name = "product/catalog.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        cache_key = 'categories'
        categories = cache.get(cache_key)
        if categories is None:
            categories = Category.objects.all()
            context[cache_key] = categories
            cache.set(cache_key, categories, 86400)
        else:
            context[cache_key] = categories

        context['products'] = Product.objects.all()

        return context
