from django.shortcuts import render
from django.views.generic import ListView
from models import Category, Product


class ProductListView(ListView):
    template_name = "product/catalog.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['products'] = Product.objects.all()
        context['categories'] = Category.objects.all()
        return context
