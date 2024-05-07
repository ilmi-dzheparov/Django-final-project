from django.contrib import admin
from .models import Product, Category, Seller, SellerProduct

admin.site.register(Product)
admin.site.register(Category)


@admin.register(Seller)
class SellerProductAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "email", "phone", "address"]
    list_display_links = ["pk", "name"]


@admin.register(SellerProduct)
class SellerProductAdmin(admin.ModelAdmin):
    list_display = ["pk", "product", "price", "quantity"]
    list_display_links = ["product"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(seller__email=request.user.email)
