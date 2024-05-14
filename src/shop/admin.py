from django.contrib import admin
from shop.models import Product, Review, Category
from shop.models import (
    Product,
    Review,
    Category,
    Attribute,
    ProductAttribute,
    Seller,
    SellerProduct
)
from .forms import AttributeFormSet, ProductAttributeFormSet, CustomAttributeAdminForm


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


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['category', 'name', 'unit']
    list_editable = ['name', 'unit']
    list_filter = ['category', ]
    fieldsets = [
        ('Категория', {
            'fields': ('category',)
        }),
        ('Характеристика', {
            'fields': ('name', 'unit')
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
    exclude = ("seller",)

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
        """
        if not change:
            obj.seller = request.user.seller
        obj.save()

