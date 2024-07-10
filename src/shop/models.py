from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import F, Sum, DecimalField
from django.urls import reverse
from taggit.managers import TaggableManager


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "shop/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


def seller_thumbnail_directory_path(instance: "Seller", filename: str) -> str:
    return f"shop/seller_thumbnails/seller_{instance.pk}/{filename}"


class HistoryProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('product__category__parent')


class HistoryProduct(models.Model):
    """
    Модель HistoryProduct представляет
    историю пользователя просмотра продуктов.
    """

    class Meta:
        ordering = ['-created_at']

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        to='Product',
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    objects = models.Manager()
    history = HistoryProductManager()


def category_icon_directory_path(instance: "Category", filename: str):
    return 'shop/icon/category_{pk}/{filename}'.format(
        pk=instance.pk,
        filename=filename
    )


class Category(models.Model):
    """
      Модель Category представляет категорию
      для модели Product, указанная ниже.
    """

    class Meta:
        ordering = ['name']
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    name = models.CharField(max_length=100, db_index=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    icon = models.ImageField(null=True, blank=True, upload_to=category_icon_directory_path)

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
        return reverse("shop:product_detail", kwargs={"pk": self.pk})


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
    Модель Attribute определяет структуру данных для хранения характеристик товаров.
    Имеет связь один-ко-многим с Category.
    Поля name (имя характеристики), unit (единица измерения), attribute_category (название категории: Экран, Общие параметры итд)

    """
    name = models.CharField(max_length=100, verbose_name='характеристика')
    unit = models.CharField(max_length=50, blank=True, default='', verbose_name='единица измерения')
    attribute_category = models.CharField(max_length=50, verbose_name='категория атрибута')
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

    def __str__(self):
        return self.value

    @property
    def attribute_name(self):
        return self.attribute.name


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
    created_at = models.DateTimeField(auto_now_add=True)
    free_delivery = models.BooleanField(default=False)
    is_limited = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name


class Cart(models.Model):
    """
    Модель Cart представляет корзину, в которую можно добавлять товары.
    """
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart number {self.id} -- User: {self.user.email} -- Total price: {self.total_price()}"

    def total_price(self):
        total = self.cart_items.aggregate(
            total=Sum(F('price') * F('quantity'), output_field=DecimalField())
        )['total'] or 0
        return total

    def add_product(self, product, quantity=1):
        cart_item, created = CartItem.objects.get_or_create(product=product, cart=self)
        if created:
            cart_item.quantity = quantity
            cart_item.price = product.price
        else:
            cart_item.quantity += quantity
        cart_item.save()

    def delete_product(self, cart_item):
        cart_item.delete()

    def update_product(self, cart_item, quantity):
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            self.delete_product(cart_item)

    def total_quantity(self):
        return self.cart_items.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0


class CartItem(models.Model):
    """
    Модель CartItem связана непосредственно с самой корзиной, описанной выше,
    данная модель обозначает кол-во, сам товар, цену.
    """
    product = models.ForeignKey('SellerProduct', on_delete=models.CASCADE, related_name='cart_items')
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"id: {self.id}. Name: {self.product.product.name} -- Cart# {self.cart.id} -- Quantity: {self.quantity} -- Price: {self.price}"


class SiteSettings(models.Model):
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='стоимость доставки')
    support_email = models.EmailField(max_length=254, verbose_name="Электронная почта поддержки", blank=True, null=True)
    popular_products_count_on_main_page = models.IntegerField(
        default=8,
        verbose_name='количество популярных товаров на главной странице',
        validators=[MaxValueValidator(100)]
    )

    products_count_in_limited_EDITION = models.IntegerField(
        default=4,
        verbose_name='количество товаров в ограниченном тираже',
        validators=[MaxValueValidator(16)]
    )

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"
