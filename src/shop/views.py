from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.cache import cache
from django.core.serializers import serialize, deserialize
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, CreateView, ListView
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.http import HttpRequest, HttpResponse
from django.db.models import Prefetch

from shop.models import Product, Review, ViewHistory, HistoryProduct
from shop.forms import ReviewForm

from shop.models import Seller, SellerProduct
from shop.mixins import NonCachingMixin


@never_cache
def history_view(request: HttpRequest, limit=10) -> HttpResponse:
    """
    Представление для отображения истории просмотра товаров.
    """

    history_products = (
        HistoryProduct.history.all()[:limit]
    )

    return render(request, 'includes/history-product.html', {
        'recently_viewed_products': history_products
    })


def update_history_product(request, product_id):
    """
    Функция update_recently_viewed реализует логику добавление товара в список просмотренных.

    При добавлении нового товара, если этот товар есть в списке просмотренных,
    он со своего места перемещается в самое начало списка. То есть в этом списке
    не может быть двух одинаковых товаров. Если этот товар и есть уже на последнем месте,
    то ничего не происходит.
    """

    if request.user.is_authenticated:
        history_products = HistoryProduct.objects.filter(user=request.user)

        if product_id in history_products.values_list('product_id', flat=True):
            history_product = history_products.get(product_id=product_id)
            history_product.created_at = timezone.now()
            history_product.save()
        else:
            HistoryProduct.objects.create(user=request.user, product_id=product_id)


class ProductDetailView(NonCachingMixin, DetailView):

    template_name = 'shop/product.html'
    context_object_name = "product"
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        product_cache_key = f'product_{self.kwargs.get("pk")}'
        product = cache.get(product_cache_key)

        if product is None:
            prefetch_reviews = Prefetch(
                lookup='reviews',
                queryset=Review.objects.select_related('author').all()
            )

            prefetch_sellers = Prefetch(
                lookup='seller_products',
                queryset=SellerProduct.objects.select_related('seller').all()
            )

            product = (Product.objects
                       .prefetch_related(prefetch_reviews, prefetch_sellers, 'category')
                       .get(pk=self.kwargs.get('pk')))

            cache.set(product_cache_key, product, timeout=60 * 60 * 24)

        update_history_product(self.request, product.id)

        items_per_page = 3
        page_number = self.request.GET.get('page')
        paginator = Paginator(product.reviews.all(), items_per_page)
        page_obj = paginator.get_page(page_number)

        context['seller_products'] = product.seller_products.all()
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
