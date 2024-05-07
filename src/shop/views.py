from django.core.cache import cache
from django.views.generic import DetailView
import json
from django.core.serializers import serialize
from models import Product


class ProductDetailView(DetailView):
    template_name = 'shop/products.html'
    context_object_name = "product"
    model = Product

    def get_object(self):
        product_cache_key = f'product_cache_key:{self.kwargs["id"]}'
        product_data = cache.get(product_cache_key)
        from django.core.serializers import serialize

        if product_data is None:
            product_data = serialize("json", Product.objects.all(), cls=ProductDetailView)

            cache.set(product_cache_key, product_data, timeout=60 * 60 * 24)
        return product_data
