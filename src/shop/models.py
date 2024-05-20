from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.conf import settings
from taggit.managers import TaggableManager


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "shop/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


def seller_thumbnail_directory_path(instance: "Seller", filename: str) -> str:
    return f"shop/seller_thumbnails/seller_{instance.pk}/{filename}"


class Category(models.Model):
    """
      Модель Category представляет категорию
      для модели Product, указанная ниже.
    """

    class Meta:
        ordering = ['name']
        verbose_name = "category"
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=100, db_index=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
      Модель Product представляет товар,
      который можно продавать в интернет-магазине.
    """

    class Meta:
        ordering = ["name"]
        verbose_name = "product"
        verbose_name_plural = "products"

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True, null=True)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    available = models.BooleanField(default=True)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_details", kwargs={"pk": self.pk})


class Review(models.Model):
    """
    Модель для хранения отзывов.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_author'
    )

    text = models.TextField(
        max_length=3000
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return f'Отзыв от {self.created_at}'


class Attribute(models.Model):
    """
    Модель Attribute  определяет структуру данных для хранения характеристик товаров.
    Имеет связь один-ко-многим с Category.
    Поля name (имя характеристики) и unit (единица измерения)
    """
    name = models.CharField(max_length=100, verbose_name='характеристика')
    unit = models.CharField(max_length=50, blank=True, default='', verbose_name='единица измерения')
    category = models.ForeignKey(Category,
                                 blank=True,
                                 null=True,
                                 related_name='attribute_names',
                                 on_delete=models.CASCADE,
                                 verbose_name='категория')

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    """
    Модель ProductAttribute связывает конкретный продукт (товар) с его характеристиками.
    Также связь с моделью Attribute.
    """

    product = models.ForeignKey(Product,
                                related_name='attributes',
                                on_delete=models.CASCADE,
                                verbose_name='товар'
                                )
    attribute = models.ForeignKey(Attribute,
                                  related_name='attributes',
                                  on_delete=models.CASCADE,
                                  verbose_name='характеристика',
                                  )
    value = models.CharField(max_length=250, verbose_name='значение')


class Seller(models.Model):
    """
    Модель Seller представляет продавца,
    который может размещать свои товары (SellerProduct) в магазине.
    """

    class Meta:
        ordering = ["name"]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="seller", on_delete=models.CASCADE)
    name = models.CharField(max_length=20, db_index=True, null=False)
    thumbnail = models.ImageField(null=True, blank=True, upload_to=seller_thumbnail_directory_path)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("seller_details", kwargs={"pk": self.pk})


class SellerProduct(models.Model):
    """
    Модель SellerProduct представляет товар, который продает конкретный продавец (Seller).
    Эта модель связана с Product и отличается ценой и количеством от продавца к продавцу.
    """

    seller = models.ForeignKey(Seller, related_name="products", on_delete=models.PROTECT)
    product = models.ForeignKey(Product, related_name="seller_products", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return self.product.name


class Cart(models.Model):
    """
    Модель Cart представляет корзину, в которую можно добавлять товары.
    """
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE)
    items = models.ManyToManyField('CartItem', related_name='cart_items')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    """
    Модель CartItem связана непосредственно с самой корзиной, описанной выше,
    данная модель обозначает кол-во, сам товар, цену.
    """
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
