from shop.models import Product, ProductAttribute, Attribute
from typing import List


class ComparisonTable:
    """
    Класс представляющий таблицу с товаром и его атрибутами, а также предоставляющий контекст для шаблона
    """
    def __init__(self, product: Product) -> None:
        self.product = product
        self.categories = []
        self.avg_price = 0
        self.msg_css_classes = ""
        self.msg_css_data_roles = ""

        self.set_average_price()

    def add_category(self, category: "ComparisonCategory") -> None:
        self.categories.append(category)

    def get_message(self):
        """
        Возвращает сообщение об состоянии рядов и категорий таблицы
        """

        # Если у переданных в сессию товаров нет ни одного общего атрибута
        if len(self.categories) == 0:
            return "Нет подходящих полей для сравнения"
        # Если в таблице есть скрытая категория (все её атрибуты одинаковы для всех продуктов),
        # то об этом выводится сообщение
        else:
            for category in self.categories:
                if category.css_data_role != "hidden":
                    self.msg_css_classes = "display_none"
                    break
            self.msg_css_data_roles = "hidden-message"
            self.msg_css_classes = "table_message"
            return "Одинаковые поля скрыты"

    def set_average_price(self):
        """
        Получаем среднюю цену товара
        """

        sum_price = 0
        seller_products = self.product.seller_products.all()
        seller_products_count = len(seller_products)

        if seller_products_count:
            for seller_product in seller_products:
                sum_price += seller_product.price
            self.avg_price = f"{float(sum_price / len(seller_products)):.2f}"
        else:
            self.avg_price = "0.00"


class ComparisonCategory:
    """
    Класс представляющий категорию атрибута в таблице
    """
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

    def set_rows(self, attributes: List[Attribute]):
        """
        Создает экземпляры ComparisonRow из переданных атрибутов (Attribute)
        """
        for attr in attributes:
            product_attrs = attr.attributes.filter(product=self.product)
            for product_attr in product_attrs:
                self.rows.append(ComparisonRow(category=self, attribute=product_attr))

    def set_hidden_by_default(self):
        """
        Устанавливает эту категорию скрытой по умолчанию
        """

        self.css_classes += "hidden_attributes"
        self.css_data_role += "hidden"

    def set_hidden_attributes(self, attributes_to_hide: List[str]):
        """
        Определяет какие ряды категории должны быть скрыты по умолчанию, исходя из переданного фильтра
        Фильтр: список из названий значений атрибутов, которые одинаковы для всех товаров в сессии
        """

        for row in self.rows:
            if row.attribute.value in attributes_to_hide:
                self.hidden_rows.append(row)
                row.set_hidden_by_default()
        self.check_active_status()

    def filter_attributes(self, attributes_filter: List[str]):
        """
        Определяет какие ряды должны быть в таблице, исходя из переданного фильтра
        Фильтр: список из названий атрибутов, которые есть не у всех переданных товаров в сессии. Такие атрибуты
        не должны быть в таблице
        """

        filtered_attributes = []

        for row in self.rows:
            if row.attribute.attribute.name in attributes_filter:
                filtered_attributes.append(row)

        self.rows = filtered_attributes
        self.check_active_status()

    def check_active_status(self):
        """
        Проверяет активность категории. Есть ли у категории нет ни одного ряда, то она не включается в таблицу
        """

        if len(self.rows) == 0:
            self.active_status = False

    def check_is_hidden_by_default(self, attributes_to_hide: List[str]):
        """
        Проверяет то, должна ли категория быть скрытой по умолчанию, исходя из фильтра
        Фильтр: список из названий значений атрибутов, которые одинаковы для всех товаров в сессии
        """

        rows_values = [row.attribute.value for row in self.rows]

        set1 = set(attributes_to_hide)
        set2 = set(rows_values)

        if len(set1 & set2) == len(self.rows):
            self.set_hidden_by_default()


class ComparisonRow:
    """
    Класс, представляющий ряд атрибута в категории
    """

    def __init__(self, category: ComparisonCategory, attribute: ProductAttribute):
        self.category = category
        self.attribute = attribute
        self.value = f"{self.attribute.value} {self.attribute.attribute.unit}"
        self.css_classes = ""
        self.css_data_role = ""

    def check_hidden_by_default(self, attr_filter: List[str]):
        """
        Проверяет должен ли быть ряд скрыт по умолчанию, исходя из фильтра
        Фильтр: список из названий значений атрибутов, которые одинаковы для всех товаров в сессии
        """

        if self.attribute.value in attr_filter:
            self.set_hidden_by_default()

    def set_hidden_by_default(self):
        """
        Устанавливает ряд скрытым по умолчанию
        """

        self.css_classes += "hidden_attributes comparis"
        self.css_data_role += "hidden"
