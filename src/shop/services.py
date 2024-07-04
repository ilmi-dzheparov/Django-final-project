from django.core.cache import cache
from django.conf import settings
from .models import Category, SellerProduct, Seller, Product
import logging
import os
import datetime
import json
import shutil
from django.db.models import Count


def setup_logger(name, log_dir, log_file, level=logging.INFO):
    os.makedirs(log_dir, exist_ok=True)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(os.path.join(log_dir, log_file))
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def import_seller_products(import_file_path):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_dir = os.path.join(settings.BASE_DIR, 'import_logs')
    logger = setup_logger('import_logger', log_dir, f'import_{timestamp}.log')

    import_successful = True

    try:
        with open(import_file_path, 'r') as file:
            import_data = json.load(file)
    except FileNotFoundError:
        logger.error(f'Файл {import_file_path} не найден.')
        return
    except json.JSONDecodeError:
        logger.error(f'Ошибка декодирования JSON из файла {import_file_path}.')
        return

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
        except Seller.DoesNotExist:
            logger.error(f"Продавец с ID {item['seller_id']} не найден.")
            import_successful = False
        except Product.DoesNotExist:
            logger.error(f"Продукт с ID {item['product_id']} не найден.")
            import_successful = False
        except KeyError as e:
            logger.error(f"Отсутствует ключ {e} в данных: {item}")
            import_successful = False
        except Exception as e:
            logger.error(f"Неизвестная ошибка при импорте продукта: {e}")
            import_successful = False

        successful_imports_dir = os.path.join(settings.BASE_DIR, 'successful_imports')
        failed_imports_dir = os.path.join(settings.BASE_DIR, 'failed_imports')

    if import_successful:
        shutil.move(import_file_path, os.path.join(successful_imports_dir, os.path.basename(import_file_path)))
    else:
        shutil.move(import_file_path, os.path.join(failed_imports_dir, os.path.basename(import_file_path)))


def get_cached_categories():
    cache_key = 'categories'
    categories = cache.get(cache_key)
    if categories is None:
        categories = Category.objects.filter(products__available=True, parent__isnull=True).distinct()
        cache.set(cache_key, categories, settings.DEFAULT_CACHE_TIME)
    return categories


def get_cached_products():
    cache_key = f'products'
    products = cache.get(cache_key)
    if products is None:

        products = SellerProduct.objects.all()

        cache.set(cache_key, products, settings.DEFAULT_CACHE_TIME)

    return products


def get_cached_popular_products():
    cache_key = 'popular_products'
    popular_products = cache.get(cache_key)

    if popular_products is None:
        product_sales = SellerProduct.objects.annotate(total_sales=Count('orders'))

        popular_products = sorted(product_sales, key=lambda p: p.total_sales, reverse=True)[:8]

        cache.set(cache_key, popular_products, settings.DEFAULT_CACHE_TIME)

    return popular_products


def get_limited_products():
    cache_key = 'limited_products'
    limited_products = cache.get(cache_key)

    if limited_products is None:
        limited_products = SellerProduct.objects.filter(is_limited=True)[:16]
        cache.set(cache_key, limited_products, settings.DEFAULT_CACHE_TIME)

    return limited_products
