from django.db import models
from shop.models import Product, Category
from django.core.validators import MinValueValidator, MaxValueValidator

DISCOUNT_WEIGHTS = [
    (1, 'Вес скидки низкий'),
    (2, 'Вес скидки средний'),
    (3, 'Вес скидки высокий')
]


class BaseDiscount(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    weight = models.IntegerField(choices=DISCOUNT_WEIGHTS)

    class Meta:
        abstract = True


class ProductDiscount(BaseDiscount):
    discount = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)],
                                   help_text="Percentage value (1 to 99", default=0)
    products = models.ManyToManyField(Product, related_name="discounts", blank=True)
    categories = models.ManyToManyField(Category, related_name="discounts", blank=True)

    def __str__(self):
        return f"product-discount-{self.name}"


class BundleDiscount(BaseDiscount):
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    product_group_1 = models.ManyToManyField(Product, related_name="products1_discounts", blank=True)
    product_group_2 = models.ManyToManyField(Product, related_name="products2_discounts", blank=True)
    category_group_1 = models.ManyToManyField(Category, related_name="categories1_discounts", blank=True)
    category_group_2 = models.ManyToManyField(Category, related_name="categories2_discounts", blank=True)

    def __str__(self):
        return f"bundle-discount-{self.name}"


class CartDiscount(BaseDiscount):
    min_quantity = models.IntegerField(default=0, help_text="Минимальное количество товаров в корзине",
                                       validators=[MinValueValidator(1)])
    max_quantity = models.IntegerField(default=0, help_text="Максимальное количество товаров в корзине")
    min_total = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                    help_text="Минимальная общая стоимость товаров в корзине")
    max_total = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                    help_text="Максимальная общая стоимость товаров в корзине")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Итоговая стоимость корзины")
