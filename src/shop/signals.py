from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Category, Product, SellerProduct, Cart, CartItem
from django.contrib.auth.signals import user_logged_in


@receiver(signal=post_save, sender=Category)
@receiver(signal=post_delete, sender=Category)
def clear_menu_cache(sender, **kwargs):
    cache.delete('categories')


@receiver(post_save, sender=Product)
def reset_cache(sender, instance, **kwargs):
    cache.delete('product_cache_key')


@receiver(post_save, sender=SellerProduct)
@receiver(post_delete, sender=SellerProduct)
def clear_product_cache(sender, **kwargs):
    keys = cache.keys('products-*')
    for key in keys:
        cache.delete(key)


@receiver(user_logged_in)
def merge_carts(sender, user, request, **kwargs):
    session_token = request.session.get('session_token')
    if not session_token:
        return

    try:
        session_cart = Cart.objects.get(token=session_token)
    except Cart.DoesNotExist:
        return

    try:
        user_cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        session_cart.user = user
        session_cart.token = None
        session_cart.save()
        return

    for item in session_cart.cart_items.all():
        user_cart.add_product(item.product, item.quantity)
    session_cart.delete()
