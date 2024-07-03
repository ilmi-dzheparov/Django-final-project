from random import choice

from datetime import datetime
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.cache import cache
from django.core.serializers import serialize, deserialize
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, CreateView, DeleteView, ListView, View, UpdateView, TemplateView
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpRequest, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse_lazy
from decimal import Decimal, InvalidOperation
from shop.utils import (
    add_to_session_cart,
    get_cart_from_session,
    get_total_price_from_session_cart,
    get_total_quantity_from_session_cart,
    remove_from_session_cart,
    update_session_cart,
)

from shop.models import (
    Product,
    Review,
    Seller,
    SellerProduct,
    Cart,
    CartItem,
    Category,
    HistoryProduct,
)
from shop.forms import ReviewForm
from django.db.models import Count
from shop.services import get_cached_popular_products, get_limited_products
from .services import get_cached_products, get_cached_categories


class IndexView(TemplateView):
    template_name = 'shop/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        popular_categories = Category.objects.annotate(product_count=Count('products')).order_by('-product_count')[:3]
        limited_products = get_limited_products()
        context['categories'] = popular_categories
        context['product'] = choice(limited_products) if len(limited_products) > 0 else None
        context['seller_products'] = get_cached_popular_products()
        context['limited_products'] = limited_products
        return context


class ProductDetailView(DetailView):
    template_name = 'shop/product_detail.html'
    context_object_name = "product_detail"
    model = Product

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            product, created = HistoryProduct.objects.get_or_create(user=request.user, product=self.get_object())

            if not created:
                product.created_at = datetime.now()
                product.save()
        return super().get(request, *args, **kwargs)

    # def get(self, request, *args, **kwargs):

    def get_object(self, queryset=None):
        product_id = self.kwargs.get("pk")
        product_cache_key = f'product_cache_key:{product_id}'
        product_data = cache.get(product_cache_key)

        if product_data is None:
            product = get_object_or_404(Product, pk=product_id)
            product_data = serialize("json", [product])
            cache.set(product_cache_key, product_data, timeout=60 * 60 * 24)
        else:
            product = list(deserialize("json", product_data))[0].object

        return product

    def get_seller_products(self, product_id):
        seller_products_cache_key = f'seller_products_cache_key:{product_id}'
        seller_products_data = cache.get(seller_products_cache_key)

        if seller_products_data is None:
            seller_products = SellerProduct.objects.filter(product_id=product_id).prefetch_related("seller")
            seller_products_data = serialize("json", seller_products)
            cache.set(seller_products_cache_key, seller_products_data, timeout=60 * 60 * 24)
        else:
            seller_products = [obj.object for obj in deserialize("json", seller_products_data)]

        return seller_products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('pk')
        context['seller_products'] = seller_products_qs = self.get_seller_products(product_id)
        price = 0
        count = 0
        min_price = 0
        min_price_id = None
        for seller_product in seller_products_qs:
            price += seller_product.price
            count += 1
            if count == 1:
                min_price_id = seller_product.id
                min_price = price
            elif count > 1:
                if price < min_price:
                    min_price = price
                    min_price_id = seller_product.id

        if count > 0:
            context['average_price'] = Decimal(price) / count
            context['min_price_id'] = min_price_id
        else:
            context['average_price'] = Decimal(0)
            context['min_price_id'] = min_price_id
        context['product_min_price_id'] = seller_products_qs

        items_per_page = 3
        page_number = self.request.GET.get('page')
        paginator = Paginator(self.object.reviews.all(), items_per_page)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['form'] = ReviewForm()
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


class AddToCartView(View):
    """
    Представление: добавление товара в корзину
    """

    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        product = get_object_or_404(SellerProduct, id=product_id)
        quantity = request.POST.get('amount', '1')
        if not quantity.isdigit():
            return HttpResponseBadRequest("Количество должно быть числом.")
        quantity = int(quantity)
        if quantity <= 0:
            return HttpResponseBadRequest("Количество должно быть больше нуля.")

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.add_product(product, quantity=quantity)
        else:
            add_to_session_cart(request, product_id, quantity)

        return redirect('shop:product_detail', product.product.id)


class CartDetailView(DetailView):
    model = Cart
    context_object_name = 'cart'
    template_name = 'shop/cart.html'

    def get_object(self, queryset=None):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
        else:
            cart = Cart()
        return cart

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart = context['cart']
            context['cart_items'] = cart.cart_items.all().prefetch_related('product')
            context['total_price'] = cart.total_price()
            context['total_quantity'] = cart.total_quantity()
        else:
            context['cart_items'] = get_cart_from_session(self.request)
            context['total_price'] = get_total_price_from_session_cart(self.request)
            context['total_quantity'] = get_total_quantity_from_session_cart(self.request)
        return context


class CartItemDeleteView(View):
    """
    Представление: удвление товара из корзины
    """

    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item = get_object_or_404(CartItem, id=product_id)
            cart.delete_product(cart_item)
        else:
            remove_from_session_cart(self.request, product_id)

        return redirect('shop:cart_detail')


class CartItemUpdateView(View):
    """
    Представление: изменение количества товара в корзине
    """

    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        quantity = request.POST.get('amount')
        if not quantity.isdigit():
            return HttpResponseBadRequest("Количество должно быть числом.")
        quantity = int(quantity)
        if quantity < 0:
            return HttpResponseBadRequest("Количество должно быть не меньше нуля.")

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            product = get_object_or_404(CartItem, id=product_id)
            cart.update_product(product, quantity=quantity)
        else:
            update_session_cart(request, product_id, quantity)

        return redirect('shop:cart_detail')


class Catalog(ListView):
    """
        Представление: каталог товаров
    """
    template_name = "shop/catalog.html"
    context_object_name = "products"
    paginate_by = 4

    def get_queryset(self):
        products = get_cached_products()
        sort_param = self.request.GET.get('sort')
        if sort_param:
            if sort_param == 'popularity':
                products = products.order_by('-popularity')
            elif sort_param == 'price':
                products = products.order_by('price')
            elif sort_param == 'reviews':
                products = products.order_by('-reviews')
            elif sort_param == 'created_at':
                products = products.order_by('-created_at')
        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = get_cached_categories()
        context['categories'] = categories
        return context
