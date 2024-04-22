from django.shortcuts import render

# Create your views here.
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
            categories = Category.objects.all().prefetch_related('products').filter(products__available=True)
            context[cache_key] = categories
            seconds_in_day = 10 ** 5
            cache.set(cache_key, categories, seconds_in_day)
        else:
            context[cache_key] = categories

        context['products'] = Product.objects.all().select_related('category')

        return context
