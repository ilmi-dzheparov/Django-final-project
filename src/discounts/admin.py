from django.contrib import admin
from .models import ProductDiscount, BundleDiscount, CartDiscount
from .forms import ProductDiscountForm, BundleDiscountForm, CartDiscountForm


@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'valid_from', 'valid_to', 'active', 'weight', 'discount']
    list_display_links = ["name"]

    form = ProductDiscountForm


@admin.register(BundleDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'valid_from', 'valid_to', 'active', 'weight', 'discount_amount']
    list_display_links = ["name"]

    form = BundleDiscountForm


@admin.register(CartDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'valid_from', 'valid_to', 'active', 'weight', 'min_quantity', 'max_quantity',
                    'min_total', 'max_total']
    list_display_links = ["name"]

    form = CartDiscountForm
