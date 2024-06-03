from django.conf import settings
from django.db import models

from shop.models import SellerProduct

PAYMENT_METHOD_CHOICES = [
    ('card', 'Онлайн картой'),
    ('account', 'Онлайн со счета'),
]


class Order(models.Model):
    """
    Модель для хранения информации о заказах.
    Она содержит поля для идентификатора заказа, связь с пользователем,
    связь с продуктом продавца, статус заказа, общую сумму заказа, дату создания, промокод и способ оплаты.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seller_product = models.ForeignKey(SellerProduct, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=50, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    promocode = models.CharField(max_length=50, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card')

    def __str__(self):
        return f"Order #{self.pk}"

    def mark_as_paid(self):
        self.order_status = 'Paid'
        self.save()

    def cancel_order(self):
        self.order_status = 'Cancelled'
        self.save()
