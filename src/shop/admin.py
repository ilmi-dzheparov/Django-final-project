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
        """
        Продавец может видеть только свои SellerProduct
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(seller__user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        При создании SellerProduct, пользователь может указать только себя в выпадающем списке seller
        """
        if db_field.name == "seller":
            seller = Seller.objects.get(user=request.user)
            kwargs["queryset"] = Seller.objects.filter(pk=seller.pk)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
