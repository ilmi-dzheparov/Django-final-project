from django.contrib import messages
from django.core.cache import cache
from django.core.serializers import serialize
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, CreateView
from django.urls import reverse
from django.utils.safestring import mark_safe

from shop.models import Product, Review
from shop.forms import ReviewForm


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


class ReviewCreateView(CreateView):
    """
    Представление: для создания отзыва к продукту.
    """

    model = Review
    form_class = ReviewForm

    def form_valid(self, form):
        review = form.save(commit=False)
        review.product_id = self.kwargs.get('pk')
        review.author = self.request.user
        review.save()
        return redirect(review.product.get_absolute_url())

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            #login_url = reverse('login')
            message = f"<p>Необходимо авторизоваться для добавления комментариев</p>"\
                      "<a href='{login_url}'>авторизоваться</a>"
            messages.info(request, mark_safe(message))
            return redirect(reverse(
                viewname='shop:product_detail',
                kwargs={'pk': self.kwargs.get('pk')}
            ))
        else:
            return super().dispatch(request, *args, **kwargs)