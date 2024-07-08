from shop.models import Product, ProductAttribute, Attribute
from .comparison_table import ComparisonTable, ComparisonCategory
from django.utils.translation import gettext_lazy as _


def delete_uniq_attribute(attributes, count):
    attribute_count = {}
    for attribute in attributes:
        attribute_count[attribute] = attribute_count.setdefault(attribute, 0) + 1

    return [attribute.name for attribute in attribute_count if attribute_count[attribute] > count - 1]


class Comparison:
    """
    Класс представляющий сервис сравнения. Он хранит данные сравниваемых товаров, фильтрует их и передает
    отфильтрованные данные таблицам (ComparisonTable - на каждый товар)
    """

    def __init__(self, request) -> None:
        self.products = []
        self.attributes = []
        self.product_attributes = []
        self.session = request.session
        comparison_products = self.session.get("comparison_service")
        if not comparison_products:
            comparison_products = self.session["comparison_service"] = []
        self.comparison_products = comparison_products

    def add(self, product_pk: int) -> None:
        """
        Добавляет в сессию переданный айди товара, если такого айди ещё нет. Если в сессии уже хранится 4 айди, то
        самое старое заменяется переданным
        """

        if product_pk not in self.comparison_products and len(self.comparison_products) < 4:
            self.comparison_products.append(product_pk)
        elif len(self.comparison_products) == 4:
            self.comparison_products.pop(0)
            self.comparison_products.append(product_pk)
        self.save()

    def remove(self, product_pk: int) -> None:
        """
        Удаляет переданное айди товара из сессии
        """

        if product_pk in self.comparison_products:
            self.comparison_products.remove(product_pk)
            self.save()

    def clear(self) -> None:
        """
        Удаляет сервис сравнения из сессии
        """

        del self.session["comparison_service"]
        self.save()

    def save(self) -> None:
        """
        Сообщает сессии, что она обновлена
        """

        self.session.modified = True

    def get_attributes_values_filter(self):
        """
        Этот метод фильтрует значения атрибутов всех товаров в сессии
        Он возвращает список названий значений атрибутов одинаковых для всех переданных товаров
        """

        attr_values_count = {}
        product_attributes = [attr.value for attr in self.product_attributes]
        products_count = len(self.products)

        for attr in product_attributes:
            attr_values_count[attr] = attr_values_count.setdefault(attr, 0) + 1

        return [val for val in attr_values_count if attr_values_count[val] == products_count]

    def service_context(self) -> dict:
        """
        Создает и передает контекст для сервиса сравнения.
        Из переданных в сессию айди находятся продукты и все связанные с ними атрибуты.
        Атрибуты фильтруются и передаются в ComparisonCategory для настройки рядков (ComparisonRow).
        Созданные ComparisonCategory передаются в таблицы (ComparisonTable)
        """

        if len(self.comparison_products) < 2:
            message = _("Недостаточно данных для сравнения. Товаров добавлено")
            return {"message": f"{message}: {len(self.comparison_products)}"}

        self.products = Product.objects.filter(id__in=self.comparison_products)
        self.product_attributes = ProductAttribute.objects.filter(product__in=self.products)
        self.attributes = Attribute.objects.filter(attributes__product__in=self.products)

        # удаляем уникальные ряды
        filtered_attributes = delete_uniq_attribute(self.attributes, len(self.products))
        # получаем одинаковые значения атрибутов для всех товаров
        filtered_values = self.get_attributes_values_filter()

        # получаем словарь, где ключ - Product, значение - Attribute и список связанных с ним ProductAttribute
        product_attributes = {}
        for product in self.products:
            attrs = Attribute.objects.filter(attributes__product=product)
            product_attributes[product] = {}
            for attr in attrs:
                if not product_attributes[product].get(attr.attribute_category, False):
                    product_attributes[product][attr.attribute_category] = []
                product_attributes[product][attr.attribute_category].append(attr)

        # проводим настройка категорий (ComparisonCategory), передавая туда фильтры и создаем таблицы (ComparisonTable)
        tables = []
        for product, categories in product_attributes.items():
            table = ComparisonTable(product=product)
            for category in categories:
                comp_category = ComparisonCategory(product=product, category_name=category,
                                                   attributes=categories[category])
                comp_category.filter_attributes(filtered_attributes)
                comp_category.set_hidden_attributes(filtered_values)
                comp_category.check_is_hidden_by_default(filtered_values)

                if comp_category.active_status:
                    table.add_category(comp_category)
            tables.append(table)

        return {"tables": tables}
