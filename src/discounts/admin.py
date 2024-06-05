from django.contrib import admin
from .models import ProductDiscount, BundleDiscount, CartDiscount

admin.site.register(ProductDiscount)
admin.site.register(BundleDiscount)
admin.site.register(CartDiscount)