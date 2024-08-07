from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from random import choice

from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.serializers import deserialize, serialize
from django.db.models import Count, Max, Min
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.cache import never_cache
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, View)
from taggit.models import Tag

from banners.models import Banner
from discounts.utils import calculate_best_discount
from shop.forms import ProductFilterForm, ReviewForm, TagsForm
from shop.mixins import NonCachingMixin
from shop.models import (Cart, CartItem, Category, HistoryProduct, Product,
                         Review, SellerProduct)
from shop.services import (get_cached_categories,
                           get_cached_popular_products, get_limited_products)
from shop.utils import (add_to_session_cart, get_cart_from_session,
                        get_total_price_from_session_cart,
                        get_total_quantity_from_session_cart,
                        remove_from_session_cart, update_session_cart)


@method_decorator(decorator=never_cache, name="get")
class IndexView(TemplateView):
    """
        Главная страница сайта
    """
    template_name = 'shop/index.html'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        popular_categories = (
            Category.objects
            .annotate(
                product_count=Count('products'),
                min_price=Min('products__seller_products__price')
            )
            .order_by('-product_count')[:3]
        )
        limited_products = get_limited_products()
        products_with_discount = [
            product for product in limited_products
            if product.product.discounts.exists()
        ]
        for product in products_with_discount:
            discount = product.product.discounts.first()
            if discount:
                discount_value = Decimal(discount.discount)
                product.price_after_discount = round(
                    product.price * (1 - discount_value / Decimal(100)), 2)

        context['popular_categories'] = popular_categories
        context['product'] = choice(products_with_discount) if products_with_discount else None
        context['seller_products'] = get_cached_popular_products()
        context['limited_products'] = limited_products
        context['banners'] = Banner.objects.filter(active=True)

        return context


class ProductDetailView(NonCachingMixin, DetailView):
    template_name = 'shop/product_detail.html'
    context_object_name = "product"
    model = Product

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            product, created = HistoryProduct.objects.get_or_create(
                user=request.user, product=self.get_object())

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
            seller_products = SellerProduct.objects.filter(
                product_id=product_id).prefetch_related('seller')
            seller_products_data = serialize('json', seller_products)
            cache.set(seller_products_cache_key, seller_products_data, timeout=60 * 60 * 24)
        else:
            seller_products = [obj.object for obj in deserialize('json', seller_products_data)]

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
                if seller_product.price < min_price:
                    min_price = seller_product.price
                    min_price_id = seller_product.id

        if count > 0:
            average_price = (price / count).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            context['average_price'] = Decimal(average_price)
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
        login_url = reverse('accounts:login')
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


@method_decorator(never_cache, name='dispatch')
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
            discount = calculate_best_discount(cart, cart.cart_items.all())
            context['total_price'] = cart.total_price() - discount
            context['total_quantity'] = cart.total_quantity()
        else:
            context['cart_items'] = get_cart_from_session(self.request)
            context['total_price'] = get_total_price_from_session_cart(self.request)
            context['total_quantity'] = get_total_quantity_from_session_cart(self.request)
        return context


class CartItemDeleteView(View):
    """
    Представление: удаление товара из корзины
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


@method_decorator(decorator=never_cache, name="get")
class CatalogProduct(ListView):
    """
    Представление выводит все продукты переданной категории.
    """
    model = SellerProduct
    template_name = "shop/catalog.html"
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        sort_param = self.request.GET.get('sort')
        selected_category_id = self.kwargs.get('pk')

        if selected_category_id:
            # Получаем категорию и её дочерние категории
            category = get_object_or_404(Category, pk=selected_category_id)
            children = category.children.all()
            queryset = SellerProduct.objects.filter(product__category__in=[category] + list(children))
        else:
            # Если категория не выбрана, возвращаем все продукты
            queryset = SellerProduct.objects.all()

        if sort_param:
            if sort_param == 'popularity':
                popular_products = get_cached_popular_products()
                popular_product_ids = [p.product_id for p in popular_products]
                queryset = queryset.filter(product__id__in=popular_product_ids)
            elif sort_param == 'price':
                queryset = queryset.order_by('price')
            elif sort_param == 'reviews':
                queryset = queryset.annotate(num_reviews=Count(
                    'product__reviews')).order_by('-num_reviews')
            elif sort_param == 'created_at':
                queryset = queryset.order_by('-created_at')

        form = ProductFilterForm(self.request.GET)
        if form.is_valid():
            price = form.cleaned_data.get('price')
            title = form.cleaned_data.get('title')
            in_stock = form.cleaned_data.get('in_stock')
            free_delivery = form.cleaned_data.get('free_delivery')

            if price:
                min_price, max_price = map(Decimal, price.split(';'))
                queryset = queryset.filter(price__range=(min_price, max_price))
            if title:
                queryset = queryset.filter(product__name__icontains=title)
            if in_stock:
                queryset = queryset.filter(quantity__gt=0)
            if free_delivery:
                queryset = queryset.filter(free_delivery=True)

        tags_form = TagsForm(self.request.GET)
        if tags_form.is_valid():
            tags = tags_form.cleaned_data.get('tags')
            if tags:
                queryset = queryset.filter(product__tags__slug__icontains=tags)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = get_cached_categories()
        context['categories'] = categories

        selected_category_id = self.kwargs.get('pk')
        selected_category = Category.objects.filter(pk=selected_category_id).first()

        if selected_category:
            selected_products = SellerProduct.objects.filter(product__category=selected_category)
        else:
            selected_products = SellerProduct.objects.all()  # Получаем все продукты, если категории нет

        max_price = selected_products.aggregate(Max('price'))['price__max']
        min_price = selected_products.aggregate(Min('price'))['price__min']
        context['data_min'] = min_price
        context['data_max'] = max_price

        tags = Tag.objects.all()
        context['tags'] = tags

        return context
