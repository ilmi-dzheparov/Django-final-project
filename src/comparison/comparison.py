from typing import List

from shop.models import Product, ProductAttribute, Attribute
from collections import Counter


# TODO можно сделать класс таблицы

def delete_uniq_attribute(attributes, count):
    attribute_count = {}
    for attribute in attributes:
        attribute_count[attribute] = attribute_count.setdefault(attribute, 0) + 1

    return [attribute.name for attribute in attribute_count if attribute_count[attribute] > count - 1]


# TODO документация


class ComparisonTable:
    rows_list = []

    def __init__(self, product: Product) -> None:
        self.product = product
        self.categories = []

    def add_category(self, category: "ComparisonCategory"):
        self.categories.append(category)


class ComparisonCategory:
    def __init__(self, product: Product, category_name: str, attributes: List[Attribute] = None):
        self.product = product
        self.category_name = category_name
        self.rows = []
        self.hidden_rows = []
        self.active_status = True
        self.css_classes = ""
        self.css_data_role = ""

        self.set_rows(attributes)

    def __iter__(self):
        for attr in self.rows:
            yield attr

    def __str__(self):
        return f"{self.category_name}: {self.rows}"

    def set_rows(self, attributes: List[Attribute]):
        for attr in attributes:
            product_attrs = attr.attributes.filter(product=self.product)
            for product_attr in product_attrs:
                self.rows.append(ComparisonRow(category=self, attribute=product_attr))

    def set_hidden_by_default(self):
        self.css_classes += "hidden_attributes"
        self.css_data_role += "hidden"

    def switch_active_status(self):
        if len(self.rows) == 0:
            self.active_status = False

    def filter_attributes(self, attributes_filter):
        filtered_attributes = []
        for row in self.rows:
            if row.attribute.attribute.name in attributes_filter:
                filtered_attributes.append(row)

        self.rows = filtered_attributes
        self.switch_active_status()

    def set_hidden_attributes(self, attributes_to_hide: List[str]):
        for row in self.rows:
            if row.attribute.value in attributes_to_hide:
                self.hidden_rows.append(row)
                row.set_hidden_by_default()
        self.switch_active_status()

    def switch_hidden_by_default(self, attributes_to_hide: List[str]):
        if len(self.rows) == len(self.hidden_rows):
            self.active_status = False
            self.set_hidden_by_default()
            return

        result = []
        rows_values = [row.attribute.value for row in self.rows]

        for key in rows_values:
            coincidence = 0
            counter1 = Counter(rows_values)
            counter2 = Counter(attributes_to_hide)
            for element in counter1:
                if element in counter2:
                    coincidence += min(counter1[element], counter2[element])

            if len(rows_values) == coincidence:
                result.append(key)

        if len(result) == len(self.rows):
            # self.hidden_by_default = True
            self.set_hidden_by_default()


class ComparisonRow:
    def __init__(self, category: ComparisonCategory, attribute: ProductAttribute):
        self.category = category
        self.attribute = attribute
        self.value = f"{self.attribute.value} {self.attribute.attribute.unit}"
        self.css_classes = ""
        self.css_data_role = ""

    def __str__(self):
        return

    def check_hidden_by_default(self, attr_filter: List[str]):
        if self.attribute.value in attr_filter:
            self.set_hidden_by_default()

    def set_hidden_by_default(self):
        self.css_classes += "hidden_attributes comparis"
        self.css_data_role += "hidden"


class Comparison:
    def __init__(self, request):
        self.products = []
        self.attributes = []
        self.product_attributes = []
        self.session = request.session
        comparison_products = self.session.get("comparison_service")
        if not comparison_products:
            comparison_products = self.session["comparison_service"] = []
        self.comparison_products = comparison_products

    def add(self, product_pk):
        if product_pk not in self.comparison_products:
            self.comparison_products.append(product_pk)
        self.save()

    def remove(self, product_pk):
        if product_pk in self.comparison_products:
            self.comparison_products.remove(product_pk)
            self.save()

    def clear(self):
        del self.session["comparison_service"]
        self.save()

    def save(self):
        self.session.modified = True

    def get_attributes_values_filter(self):
        # TODO возможно переделать
        """
        #TODO возвращает названия одинаковых аттрибутов у товаров, которые должны быть скрыты по умолчанию
        """
        same_attr_values_count = {}
        product_attributes = [attr.value for attr in list(self.product_attributes)]
        products_count = len(self.products)

        while product_attributes:
            current = product_attributes[0]
            product_attributes.remove(current)
            for attr in product_attributes:
                if attr == current:
                    same_attr_values_count[current] = same_attr_values_count.setdefault(current, 1) + 1
                    break

        return [val for val in same_attr_values_count if same_attr_values_count[val] == products_count]

    def service_context(self):
        """
        #TODO
        """

        if not self.comparison_products:
            return {}

        self.products = Product.objects.filter(id__in=self.comparison_products)
        self.product_attributes = ProductAttribute.objects.filter(product__in=self.products)
        self.attributes = Attribute.objects.filter(attributes__product__in=self.products)

        # удаляем уникальные ряды (нет такого уже у других товаров)
        filtered_attributes = delete_uniq_attribute(self.attributes, len(self.products))
        filtered_values = self.get_attributes_values_filter()

        product_attributes = {}
        for product in self.products:
            attrs = Attribute.objects.filter(attributes__product=product)
            product_attributes[product] = {}
            for attr in attrs:
                if not product_attributes[product].get(attr.attribute_category, False):
                    product_attributes[product][attr.attribute_category] = []
                product_attributes[product][attr.attribute_category].append(attr)

        tables = []
        for product, categories in product_attributes.items():
            table = ComparisonTable(product=product)
            for category in categories:
                comp_category = ComparisonCategory(product=product, category_name=category,
                                                   attributes=categories[category])
                comp_category.switch_hidden_by_default(filtered_values)
                comp_category.filter_attributes(filtered_attributes)
                comp_category.set_hidden_attributes(filtered_values)
                table.add_category(comp_category)
            tables.append(table)

        return {"tables": tables}
