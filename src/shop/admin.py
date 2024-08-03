from django.contrib import admin
from django.urls import path

from .forms import (AttributeFormSet, CustomAttributeAdminForm,
                    ProductAttributeFormSet)
from .models import (Attribute, Cart, CartItem, Category, HistoryProduct,
                     Product, ProductAttribute, Review, Seller, SellerProduct,
                     SiteSettings)
from .utils import (import_json, reset_cache_all, reset_cache_products,
                    reset_cache_seller_products)


@admin.register(HistoryProduct)
class HistoryProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_select_related = ['product', 'user']

    def has_add_permission(self, request):
        """
        Метод запрещает создавать историю просмотра в админ-панели
        """

        return False

    def has_change_permission(self, request, obj=None):
        """
        Метод запрещает изменять историю просмотра в админ-панели.
        """

        return False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'author', 'review', 'created_at']
    list_select_related = ['product', 'author']
    search_fields = ('product__name',)
    list_filter = ['created_at']

    def has_add_permission(self, request):
        """
        Метод запрещает создавать комментарии в админ-панели
        """

        return False

    def has_change_permission(self, request, obj=None):
        """
        Метод запрещает изменять комментарии в админ-панели
        """

        return False

    def get_search_results(self, request, queryset, search_term):
        """
        Метод для получения результатов поиска по заданному запросу.
        """

        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset |= self.model.objects.filter(product__name__icontains=search_term)
        return queryset, use_distinct

    def review(self, obj):
        """
        Метод ограничивает длину отображаемых символов до "100"
        """

        return (obj.text[:100] + '...') if len(obj.text) > 100 else obj.text


class AttributesInLine(admin.TabularInline):
    """
    Инлайн-форма создания attributes (характеристик), которая буде добавлена в админ панель модели Category
    """

    model = Attribute
    formset = AttributeFormSet
    extra = 1


class ProductAttributeInline(admin.TabularInline):
    """
    Создание инлайновой формы добавления характеристик в административной панели Django.
    Родительская модель Product
    """
    model = ProductAttribute
    formset = ProductAttributeFormSet
    extra = 1

    """
    Настройки виджета полей ForeignKey attribute (характеристика) в административной панели Djangoю
    Цель: при выборе attribute доступны только attriutes (характреристики), которые связаны с категорией товара
    """

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "attribute":
            # Получаем категорию товара, для которого создается или редактируется атрибут
            product_id = request.resolver_match.kwargs.get('object_id')
            if product_id:
                product = Product.objects.get(pk=product_id)
                product_category = product.category
                # Фильтруем характеристики по категории товара
                kwargs["queryset"] = Attribute.objects.filter(category=product_category)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductAttributeInline]
    """
       Метод get_formsets_with_inlines определяет какие формы и inline-формы будут отображаться
       на странице изменения объекта в административной панели Django.
       Переопределяем метод, чтоб инлайн-форма отображалась если редактируем объект.
       При создании объекта форма не будет отображаться
       """

    def get_formsets_with_inlines(self, request, obj=None):
        if obj:
            return super().get_formsets_with_inlines(request, obj)
        return []


class CategoryAdmin(admin.ModelAdmin):
    inlines = [AttributesInLine]


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['category', 'name', 'unit', 'attribute_category']
    list_editable = ['name', 'unit', 'attribute_category']
    list_filter = ['category', ]
    fieldsets = [
        ('Категория', {
            'fields': ('category',)
        }),
        ('Характеристика', {
            'fields': ('name', 'unit', 'attribute_category')
        }),
    ]

    form = CustomAttributeAdminForm


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "email", "phone", "address"]
    list_display_links = ["pk", "name"]


@admin.register(SellerProduct)
class SellerProductAdmin(admin.ModelAdmin):
    list_display = ["pk", "product", "price", "quantity"]
    list_display_links = ["product"]
    change_list_template = "shop/admin/change-list.html"

    def get_queryset(self, request):
        """
        Продавец может видеть только свои SellerProduct
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(seller__user=request.user)

    def save_model(self, request, obj, form, change):
        """
        Текущий пользователь указывается как Seller для созданного SellerProduct
        Суперпользователь может выбирать из выпадающего списка Seller для SellerProduct
        """
        if not change and not request.user.is_superuser:
            obj.seller = request.user.seller
        obj.save()

    def get_exclude(self, request, obj=None):
        """
        Если не суперпользователь, то выпадающий список со всеми Seller отсутствует
        """
        if not request.user.is_superuser:
            return ("seller",)
        return super().get_exclude(request, obj)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    change_list_template = "shop/admin/settings_changelist.html"
    list_display = [field.name for field in SiteSettings._meta.get_fields()]

    def has_add_permission(self, request):
        # Запрет добавление записи, если уже существует одна
        if SiteSettings.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        # Запрет удаления записи
        return False

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import_settings/",
                import_json,
                name="import_settings_json",
            ),
            path(
                "reset_cache_all/",
                reset_cache_all,
                name="reset_cache_all",
            ),
            path(
                "reset_cache_products/",
                reset_cache_products,
                name="reset_cache_products",
            ),
            path(
                "reset_cache_seller_products/",
                reset_cache_seller_products,
                name="reset_cache_seller_products",
            ),
        ]
        return new_urls + urls
