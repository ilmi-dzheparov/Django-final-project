from django.views.generic import ListView, DetailView

from .models import BaseDiscount


class DiscountListView(ListView):
    model = BaseDiscount
    template_name = 'shop/discount.html'


class DiscountDetailView(DetailView):
    model = BaseDiscount
    template_name = 'discount_detail.html'
