from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
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
        verbose_name_plural = "shop"

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True, null=True)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='shop')
    available = models.BooleanField(default=True)
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_details", kwargs={"pk": self.pk})


class Seller(models.Model):
    """
    Модель Seller представляет продавца,
    который может размещать свои товары (SellerProduct) в магазине.
    """

    class Meta:
        ordering = ["name"]

    user = models.OneToOneField(User, related_name="seller", on_delete=models.CASCADE)
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
