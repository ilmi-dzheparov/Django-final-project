from shop.models import Cart, CartItem, SellerProduct
from django.shortcuts import get_object_or_404
from decimal import Decimal


"""
Методы для работы с корзиной неаторизованного пользователя в сессии
"""
def get_cart_from_session(request):
    cart = request.session.get('cart', {})
    cart_items_objs = []
    for key, value in cart.items():
        product = SellerProduct.objects.get(pk=int(key))
        cart_item = CartItem(id=int(key), product=product, quantity=cart[key]['quantity'],
                             price=Decimal(cart[key]['price']))
        cart_items_objs.append(cart_item)
    return cart_items_objs


def save_cart_to_session(request, cart):
    request.session['cart'] = cart


def add_to_session_cart(request, product_id, quantity):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        product = get_object_or_404(SellerProduct, pk=product_id)
        cart[str(product_id)] = {
            'quantity': quantity,
            'price': str(product.price),
        }
    save_cart_to_session(request, cart)


def get_total_price_from_session_cart(request):
    cart = request.session.get('cart', {})
    total_price = 0
    for key, value in cart.items():
        total_price += Decimal(value['quantity'] * Decimal(value['price']))
    return total_price


def get_total_quantity_from_session_cart(request):
    cart = request.session.get('cart', {})
    total_quantity = 0
    for key, value in cart.items():
        total_quantity += value['quantity']
    return total_quantity


def remove_from_session_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        save_cart_to_session(request, cart)


def update_session_cart(request, product_id, quantity):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        if quantity > 0:
            cart[str(product_id)]['quantity'] = quantity
        else:
            remove_from_session_cart(request, product_id)
        save_cart_to_session(request, cart)


def clear_session_cart(request):
    save_cart_to_session(request, {})
