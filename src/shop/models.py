from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "shop/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


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


@receiver(signal=post_save, sender=Category)
@receiver(signal=post_delete, sender=Category)
def clear_menu_cache(sender, **kwargs):
    cache.delete('categories')


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
