from django.db import models


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Category(models.Model):
    """
      Модель Category представляет категорию
      для модели Product, указанная ниже.
    """
    name = models.CharField(max_length=100, db_index=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
      Модель Product представляет товар,
      который можно продавать в интернет-магазине.
    """

    class Meta:
        ordering = ["name", "price"]
        verbose_name = "product"
        verbose_name_plural = "products"

    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=False, blank=True, db_index=True)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sellers_count = models.PositiveIntegerField()
    reviews_count = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
