from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.cache import cache
from django.core.serializers import serialize, deserialize
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, CreateView
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpRequest
from django.views.generic import ListView

from shop.models import Product, Review, ViewHistory
from shop.forms import ReviewForm

from shop.models import Seller, SellerProduct


class ProductDetailView(DetailView):
    template_name = 'shop/product.html'
    context_object_name = "product"
    model = Product

    # def get_object(self, queryset=None):
    #     product = get_object_or_404(Product, pk=self.kwargs.get("pk"))
    #     product_cache_key = f'product_cache_key:{product.id}'
    #     product_data = cache.get(product_cache_key)
    #
    #     if product_data is None:
    #         product_data = serialize("json", [product])
    #         cache.set(product_cache_key, product_data, timeout=60 * 60 * 24)
    #     return product_data

    def get_object(self, queryset=None):
        product_id = self.kwargs.get("pk")
        product_cache_key = f'product_cache_key:{product_id}'

        product_data = cache.get(product_cache_key)

        if product_data is None:
            product = get_object_or_404(Product, pk=product_id)
            product_data = serialize('json', [product])
            cache.set(product_cache_key, product_data, timeout=60 * 60 * 24)
        else:
            product = list(deserialize('json', product_data))[0].object

        return product

    def dispatch(self, request, *args, **kwargs):
        # Record the view history
        response = super().dispatch(request, *args, **kwargs)
        if request.user.is_authenticated:
            product = self.get_object()
            ViewHistory.objects.create(user=request.user, product=product)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('pk')
        context['seller_products'] = SellerProduct.objects.filter(product_id=product_id).prefetch_related("seller")
        return context


class ReviewCreateView(PermissionRequiredMixin, CreateView):
    """
    Представление: для создания отзыва к продукту.
    """

    model = Review
    form_class = ReviewForm
    permission_required = 'auth.is_authenticated'

    def form_valid(self, form):
        review = form.save(commit=False)
        review.product_id = self.kwargs.get('pk')
        review.author = self.request.user
        review.save()
        return redirect(review.product.get_absolute_url())

    def handle_no_permission(self):
        login_url = reverse('login')
        message = mark_safe(
            f"<p>Необходимо авторизоваться для добавления комментариев</p>"
            f"<a href='{login_url}'>авторизоваться</a>"
        )
        messages.info(self.request, message)
        return redirect(reverse(
            viewname='shop:product_detail',
            kwargs={'pk': self.kwargs.get('pk')}
        ))
