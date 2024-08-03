from django import forms

from shop.models import Category, Product

from .models import BundleDiscount, CartDiscount, ProductDiscount
from .utils import (check_dates_of_discount,
                    check_if_products_belong_to_categories_of_another_group,
                    check_if_products_categories_exist)

PRODUCTS = forms.ModelMultipleChoiceField(queryset=Product.objects.filter(seller_products__isnull=False).distinct(),
                                          widget=forms.CheckboxSelectMultiple,
                                          required=False)
CATEGORIES = forms.ModelMultipleChoiceField(queryset=Category.objects.all(),
                                            widget=forms.CheckboxSelectMultiple,
                                            required=False)


class ProductDiscountForm(forms.ModelForm):
    products = PRODUCTS
    categories = CATEGORIES

    class Meta:
        model = ProductDiscount
        fields = ['name', 'discount', 'description', 'valid_from', 'valid_to', 'active', 'weight', 'discount', 'products',
                  'categories']

    def clean(self):
        cleaned_data = super().clean()
        check_dates_of_discount(cleaned_data)
        # products = cleaned_data.get("products")
        # categories = cleaned_data.get("categories")
        #
        # # Проверка наличия продуктов в скидке
        # check_if_products_categories_exist(products, categories)
        return cleaned_data


class BundleDiscountForm(forms.ModelForm):
    product_group_1 = PRODUCTS
    product_group_2 = PRODUCTS
    category_group_1 = CATEGORIES
    category_group_2 = CATEGORIES

    class Meta:
        model = BundleDiscount
        fields = ['name', 'description', 'valid_from', 'valid_to', 'active', 'weight', 'discount_amount',
                  'product_group_1',
                  'product_group_2', 'category_group_1', 'category_group_2']

    def clean(self):
        cleaned_data = super().clean()

        # Проверка, чтоб дата окончания скидки была больше даты начала скидки
        check_dates_of_discount(cleaned_data)

        products_1 = cleaned_data.get("product_group_1")
        products_2 = cleaned_data.get("product_group_2")
        categories_1 = cleaned_data.get("category_group_1")
        categories_2 = cleaned_data.get("category_group_2")

        # Проверка наличия продуктов в обеих группах в скидке
        check_if_products_categories_exist(products_1, categories_1, "in group 1")
        check_if_products_categories_exist(products_2, categories_2, "in group 2")

        # Проверка наличия одинаковых выбранных категорий в обеих группах
        categories_set_group_1 = set(categories_1)
        categories_set_group_2 = set(categories_2)
        if categories_set_group_1.intersection(categories_set_group_2):
            raise forms.ValidationError("Some selected categories belong to the both groups.")

        # Проверка наличия продуктов из одной группы в категориях из другой группы
        check_if_products_belong_to_categories_of_another_group(products_1, categories_2, (1, 2))
        check_if_products_belong_to_categories_of_another_group(products_2, categories_1, (2, 1))

        # Проверка наличия одинаковых продуктов в выбранных продуктах обеих группах
        products_intersection = set(products_1).intersection(set(products_2))
        if products_intersection:
            raise forms.ValidationError(
                f"Some selected products {products_intersection} belong to the products in both groups.")

        return cleaned_data


class CartDiscountForm(forms.ModelForm):
    class Meta:
        model = CartDiscount
        fields = ['name', 'description', 'valid_from', 'valid_to', 'active', 'weight', 'min_quantity', 'max_quantity',
                  'min_total', 'max_total', 'discount_price']

    def clean(self):
        cleaned_data = super().clean()

        # Проверка, чтоб дата окончания скидки была больше даты начала скидки
        check_dates_of_discount(cleaned_data)

        # Проверка, чтоб максимальное количество товаров в корзине было больше минимального количества
        min_quantity = cleaned_data.get("min_quantity")
        max_quantity = cleaned_data.get("max_quantity")
        if min_quantity and max_quantity:
            if min_quantity <= 0:
                raise forms.ValidationError(
                    "The minimum quantity of products in the cat must be greater than or equal to 1."
                )
            if min_quantity >= max_quantity:
                raise forms.ValidationError(
                    "The maximum quantity of products in the cat must be greater then the minimum quantity."
                )

        # Проверка, чтоб максимальная стоимость товаров в корзине была больше минимальной стоимости корзины
        min_total = cleaned_data.get("min_total")
        max_total = cleaned_data.get("max_total")
        if min_total and max_total:
            if min_total <= 0:
                raise forms.ValidationError(
                    "The minimum total price of the cart must be greater then 0."
                )
            if min_total >= max_total:
                raise forms.ValidationError(
                    "The maximum total price of the cart must be greater then the minimum total price."
                )
