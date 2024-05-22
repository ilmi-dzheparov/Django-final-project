from django.core.cache import cache
from django.conf import settings
from .models import Category, SellerProduct, Seller, Product
import logging
import os
import datetime
import json
import shutil


def import_seller_products(import_file_path):
    logger = logging.getLogger('import_logger')
    logger.setLevel(logging.INFO)
    log_dir = os.path.join(settings.BASE_DIR, 'import_logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    fh = logging.FileHandler(os.path.join(log_dir, f'import_{timestamp}.log'))
    fh.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)

    import_successful = True

    import_data = json.loads(import_file_path)

    for item in import_data:
        try:
            seller = Seller.objects.get(id=item['seller_id'])
            product = Product.objects.get(id=item['product_id'])
            price = item['price']
            quantity = item['quantity']
            created_at = item['created_at']

            seller_product = SellerProduct(
                seller=seller,
                product=product,
                price=price,
                quantity=quantity,
                created_at=created_at,
            )
            seller_product.save()
            logger.info(f'Продукт {product} успешно импортирован.')
        except:
            logger.error(f"Продавец или продукт с указанными идентификаторами не найден: {item}")
            import_successful = False

        successful_imports_dir = os.path.join(settings.BASE_DIR, '/successful_imports')
        failed_imports_dir = os.path.join(settings.BASE_DIR, '/failed_imports')

        if import_successful:
            shutil.move(import_file_path, os.path.join(successful_imports_dir, os.path.basename(import_file_path)))
        else:
            shutil.move(import_file_path, os.path.join(failed_imports_dir, os.path.basename(import_file_path)))

        logger.removeHandler(fh)


def get_cached_categories():
    cache_key = 'categories'
    categories = cache.get(cache_key)
    if categories is None:
        categories = Category.objects.filter(products__available=True).prefetch_related('products')
        cache.set(cache_key, categories, settings.DEFAULT_CACHE_TIME)
    return categories


def get_cached_products(tag, sort):
    cache_key = f'products-{sort}-{tag}'
    products = cache.get(cache_key)
    if products is None:

        products = SellerProduct.objects.all()

        if sort:
            products = products.order_by(sort)

        if tag:
            products = products.filter(tags__name=tag)

        cache.set(cache_key, products, settings.DEFAULT_CACHE_TIME)

    return products
