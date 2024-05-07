from django.core.cache import cache
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from shop.models import Product


class ProductDetailView(DetailView):
    template_name = 'shop/product.html'
    context_object_name = "product"
    model = Product

    def get_object(self, queryset=None):
        product = get_object_or_404(Product, pk=self.kwargs.get("pk"))
        product_cache_key = f'product_cache_key:{product.id}'
        product_data = cache.get(product_cache_key)

        if product_data is None:
            product_data = serialize("json", [product])
            cache.set(product_cache_key, product_data, timeout=60 * 60 * 24)
        return product_data
