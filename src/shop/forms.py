from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms import BaseInlineFormSet

from shop.admin_mixin import UniqueAttributeMixin
from shop.models import Attribute, ProductAttribute, Review


class CustomAttributeAdminForm(forms.ModelForm):
    """
    Переопределяем метод clean для валидации ввода данных (исключить дублирование записей независимо от регистра)
    Переопределим нашу кастомную форму CustomAttributeAdminForm, которая содержит метод clean.

    """

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        category = cleaned_data.get("category")

        if name and category:
            # Создаем Q-объекты для фильтрации по имени и категории с игнорированием регистра
            name_query = Q(name__iexact=name)
            category_query = Q(category=category)

            # Исключаем текущую характеристику из результата (если объект уже существует)
            if self.instance:
                existing_attributes = Attribute.objects.filter(
                    ~Q(pk=self.instance.pk), name_query, category_query
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


class AttributeFormSet(BaseInlineFormSet, UniqueAttributeMixin):
    """
    Создание класса, который наследует функциональность базового набора форм.
    Переопределим метод clean, чтобы добавить собственные правила валидации и обработки данныхю.
    При создании дубликата характеристики в инлайн форме при сохранениии появляется ValidationError.
    """

    class Meta:
        model = Attribute
        fields = '__all__'

    field_name = 'name'

    def clean(self):
        self.check_unique_attribute_name(self.forms, self.errors)


class ProductAttributeFormSet(BaseInlineFormSet, UniqueAttributeMixin):
    """
    Создание класса, который наследует функциональность базового набора форм.
    Переопределим метод clean, чтобы добавить собственные правила валидации и обработки данныхю.
    При создании дубликата характеристики в инлайн форме при сохранениии появляется ValidationError.
    """

    class Meta:
        model = ProductAttribute
        fields = '__all__'

    field_name = 'attribute'

    def clean(self):
        self.check_unique_attribute_name(self.forms, self.errors)


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['text'].widget.attrs.update({
            'name': "review",
            'id': "review",
            'placeholder': 'Отзывы',
            'class': 'form-textarea'
        })
        self.fields['text'].label = False
