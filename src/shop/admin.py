from django.contrib import admin
from .models import Product, Attribute, ProductAttribute, Category
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import BaseInlineFormSet


admin.site.register(Product)


class AttributeFormSet(BaseInlineFormSet):
    """
    Создание класса, который наследует функциональность базового набора форм.
    Переопределим метод clean, чтобы добавить собственные правила валидации и обработки данных.
    При создании дубликата характеристики в инлайн форме при сохранениии появляется ValidationError.
    """

    class Meta:
        model = Attribute
        fields = "__all__"

    def clean(self):
        if any(self.errors):
            # Если есть другие ошибки, не выполняем дополнительную проверку
            return
        attribute_names = set()
        for form in self.forms:
            if form.cleaned_data:
                attribute_name = form.cleaned_data["name"].lower()
                # Проверяем, есть ли такая комбинация товара и характеристики
                if attribute_name in attribute_names:
                    raise ValidationError(
                        "Вы добавляете характеристику товара, которая уже существует, или создаете "
                        "несколько дублирующих характеристик"
                    )
                attribute_names.add(attribute_name)


class AttributesInLine(admin.TabularInline):
    """
    Инлайн-форма создания attributes (характеристик), которая буде добавлена в админ панель модели Category
    """
    model = Attribute
    formset = AttributeFormSet
    extra = 1


class ProductAttributeFormSet(BaseInlineFormSet):
    """
    Создание класса, который наследует функциональность базового набора форм.
    Переопределим метод clean, чтобы добавить собственные правила валидации и обработки данныхю.
    При создании дубликата характеристики в инлайн форме при сохранениии появляется ValidationError.
    """

    class Meta:
        model = ProductAttribute
        fields = "__all__"

    def clean(self):
        if any(self.errors):
            # Если есть другие ошибки, не выполняем дополнительную проверку
            return
        attributes = set()
        for form in self.forms:
            if form.cleaned_data:
                attribute = form.cleaned_data["attribute"]
                # Проверяем, есть ли такая комбинация товара и характеристики
                if attribute in attributes:
                    raise ValidationError(
                        "Вы добавляете характеристику товара, которая уже существует, или создаете "
                        "несколько дублирующих характеристик"
                    )
                attributes.add(attribute)


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
            product_id = request.resolver_match.kwargs.get("object_id")
            if product_id:
                product = Product.objects.get(pk=product_id)
                print(product)
                product_category = product.category
                # Фильтруем характеристики по категории товара
                kwargs["queryset"] = Attribute.objects.filter(category=product_category)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    inlines = [
        AttributesInLine,
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    inlines = [
        ProductAttributeInline,
    ]


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    """
    Интеграция в админ панель модели Attribute
    """

    list_display = ["category", "name", "unit"]
    list_editable = ["name", "unit"]
    list_filter = [
        "category",
    ]
    fieldsets = [
        ("Категория", {"fields": ("category",)}),
        ("Характеристика", {"fields": ("name", "unit")}),
    ]

    """
    Переопределяем метод clean для валидации ввода данных (исключить дублирование записей независимо от регистра) 
    Переопределим метод get_form, чтобы возвращать нашу кастомную форму CustomAttributeAdminForm(form), которая содержит метод clean.

    """
    def get_form(self, request, obj=None, **kwargs):
        # Получаем форму, связанную с административной панелью
        form = super().get_form(request, obj, **kwargs)

        class CustomAttributeAdminForm(form):
            def clean(self):
                cleaned_data = super().clean()
                name = cleaned_data.get("name")
                category = cleaned_data.get("category")

                if name and category:
                    # Создаем Q-объекты для фильтрации по имени и категории с игнорированием регистра
                    name_query = Q(name__iexact=name)
                    category_query = Q(category=category)

                    # Исключаем текущую характеристику из результата (если объект уже существует)
                    if obj:
                        existing_attributes = Attribute.objects.filter(
                            ~Q(pk=obj.pk), name_query, category_query
                        )
                    else:
                        existing_attributes = Attribute.objects.filter(
                            name_query, category_query
                        )

                    # Проверяем, есть ли уже характеристика с таким именем в рамках текущей категории (игнорируя регистр)
                    if existing_attributes.exists():
                        raise ValidationError(
                            "Характеристика с таким именем уже существует в данной категории."
                        )

                return cleaned_data

        return CustomAttributeAdminForm
