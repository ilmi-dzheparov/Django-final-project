from django import forms
from discounts.models import ProductDiscount, CartDiscount, BundleDiscount
from shop.models import Product


# Проверка, чтоб дата окончания скидки была больше даты начала скидки
def check_dates_of_discount(cleaned_data):
    valid_from = cleaned_data.get("valid_from")
    valid_to = cleaned_data.get("valid_to")

    if valid_from and valid_to:
        if valid_from >= valid_to:
            raise forms.ValidationError("The end date must be after the start date.")


# Проверка наличия продуктов в скидке
def check_if_products_categories_exist(products, categories, group_name=''):
    if not products and not categories:
        raise forms.ValidationError(f"The products or the categories must be chosen {group_name}.")

    categories_products_list = []
    for category in categories:
        categories_products_list += [item for item in category.products.all()]

    if not products and categories:
        if not categories_products_list:
            raise forms.ValidationError(f"The chosen categories {group_name} do not contain products.")


# Проверка наличия продуктов из одной группы в категориях из другой группы
def check_if_products_belong_to_categories_of_another_group(products, categories, group_nums=(1, 2)):
    products_in_categories_of_another_group = set()
    for category in categories:
        products_in_categories_of_another_group.update(category.products.all())
    products_intersection = set(products).intersection(products_in_categories_of_another_group)
    if products_intersection:
        raise forms.ValidationError(
            f"Products {products_intersection} from group {group_nums[0]} belong to categories of group {group_nums[1]}."
        )


def calculate_product_discounts(cart_items):
    total_discount = 0

    for item in cart_items:
        product = item.product
        quantity = item.quantity

        # Получаем скидку, связанную с данным продуктом
        product_discount = ProductDiscount.objects.filter(products__in=[product.product]).first()

        # Если у продукта нет скидки, проверяем, входит ли он в категорию со скидкой
        if not product_discount:
            product_discount = ProductDiscount.objects.filter(categories__in=[product.product.category]).first()

        if product_discount:
            # Проверяем даты действия скидки
            check_dates_of_discount({
                'valid_from': product_discount.valid_from,
                'valid_to': product_discount.valid_to
            })

            # Вычисляем сумму скидки для данного продукта и добавляем ее к общей сумме
            discount_amount = (product.price * product_discount.discount * quantity) / 100
            total_discount += discount_amount

    return total_discount



def calculate_cart_discount(cart):
    # Получаем активную скидку на данную корзину
    cart_discount = CartDiscount.objects.filter(carts=cart, active=True).first()

    if cart_discount:
        # Проверяем даты действия скидки
        check_dates_of_discount({
            'valid_from': cart_discount.valid_from,
            'valid_to': cart_discount.valid_to
        })

        # Проверяем, соответствует ли корзина условиям скидки
        if (cart_discount.min_quantity <= cart.total_quantity() <= cart_discount.max_quantity and
                cart_discount.min_total <= cart.total_price() <= cart_discount.max_total):
            # Вычисляем сумму скидки
            discount_amount = max(cart.total_price() - cart_discount.discount_price, 0)
            return discount_amount

    return 0


def apply_best_bundle_discount(cart):
    # Получаем все активные скидки на наборы
    bundle_discounts = BundleDiscount.objects.filter(active=True)

    best_discount_amount = 0

    # Проходим по всем скидкам на наборы
    for discount in bundle_discounts:
        # Получаем все товары в корзине из первой и второй группы товаров
        cart_items_group_1 = cart.cart_items.filter(product__product__in=discount.product_group_1.all())
        cart_items_group_2 = cart.cart_items.filter(product__product__in=discount.product_group_2.all())

        # Если в корзине есть товары из обеих групп, то скидка может быть применена
        if cart_items_group_1.exists() and cart_items_group_2.exists():
            # Если сумма скидки больше, чем у предыдущей лучшей скидки, то обновляем лучшую скидку
            if discount.discount_amount > best_discount_amount:
                best_discount_amount = discount.discount_amount

    return best_discount_amount


def calculate_best_discount(cart, cart_items):
    # Вычисляем сумму каждой скидки
    product_discount = calculate_product_discounts(cart_items)
    cart_discount = calculate_cart_discount(cart)
    bundle_discount = apply_best_bundle_discount(cart)

    # Находим максимальную сумму скидки
    max_discount = max(product_discount, cart_discount, bundle_discount)

    return max_discount
