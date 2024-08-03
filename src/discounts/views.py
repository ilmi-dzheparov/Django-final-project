from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, TemplateView

from .models import BundleDiscount, CartDiscount, ProductDiscount


@method_decorator(decorator=never_cache, name="get")
class DiscountListView(TemplateView):
    template_name = 'shop/discount.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_discount_list'] = ProductDiscount.objects.all()
        context['bundle_discount_list'] = BundleDiscount.objects.all()
        context['cart_discount_list'] = CartDiscount.objects.all()
        return context


class ProductDiscountDetailView(DetailView):
    model = ProductDiscount
    template_name = 'shop/discount_detail.html'


class BundleDiscountDetailView(DetailView):
    model = BundleDiscount
    template_name = 'shop/discount_detail.html'


class CartDiscountDetailView(DetailView):
    model = CartDiscount
    template_name = 'shop/discount_detail.html'
