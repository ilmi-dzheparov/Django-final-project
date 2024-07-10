from django import forms


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
