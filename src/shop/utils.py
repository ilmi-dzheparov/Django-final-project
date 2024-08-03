import json
from decimal import Decimal

from django.contrib import messages
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from shop.forms import JSONImportForm
from shop.models import CartItem, Product, SellerProduct, SiteSettings

"""
Методы для работы с корзиной неавторизованного пользователя в сессии
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


def import_json(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        form = JSONImportForm
        context = {
            "form": form,
        }
        return render(request, "shop/admin/json_form.html", context)

    form = JSONImportForm(request.POST, request.FILES)
    if not form.is_valid():
        context = {
            "form": form,
        }
        return render(request, "shop/admin/json_form.html", context, status=400)

    json_file = form.cleaned_data['json_file']
    data = json.load(json_file)
    site_settings, created = SiteSettings.objects.get_or_create()
    for setting, value in data.items():
        if hasattr(site_settings, setting):
            setattr(site_settings, setting, value)
        else:
            return HttpResponse(f"Ошибка: Настройка '{setting}' не существует.", status=400)
    site_settings.save()
    messages.success(request, "Настройки успешно загружены из JSON файла.")
    return redirect("..")


def reset_cache_all(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        cache.clear()
        messages.success(request, "Весь кэш успешно сброшен.")
    return redirect('..')


def reset_cache_products(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        for product in Product.objects.all():
            cache_key = f'product_cache_key:{product.id}'
            cache.delete(cache_key)
        messages.success(request, "Кэш для товаров сброшен.")
    return redirect('..')


def reset_cache_seller_products(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        for product in SellerProduct.objects.all():
            cache_key = f'product_cache_key:{product.id}'
            cache.delete(cache_key)
        messages.success(request, "Кэш для товаров продавцов сброшен.")
    return redirect('..')
