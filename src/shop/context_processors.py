from .services import get_cached_categories, get_cached_products
from .models import Cart
from .utils import get_total_quantity_from_session_cart, get_total_price_from_session_cart


def categories(request):
    return {'categories': get_cached_categories()}


def products(request, tag, sort):
    return {f'products-{sort}-{tag}': get_cached_products(tag, sort)}


def info_cart(request):
    total_quantity = 0
    total_price = 0

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        total_quantity = cart.total_quantity()
        total_price = cart.total_price()
    else:
        total_quantity = get_total_quantity_from_session_cart(request)
        total_price = get_total_price_from_session_cart(request)

    return {'total_quantity': total_quantity, 'total_price': total_price}
