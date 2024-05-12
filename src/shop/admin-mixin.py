from django.core.exceptions import ValidationError


class UniqueAttributeMixin:
    """
    Миксин для валидации дублирования характеристик товаров при добавлении в инлайн форме
    """
    field_name = None

    def check_unique_attribute_name(self, forms, errors):
        if any(errors):
            return
        attribute_names = set()
        for form in forms:
            if form.cleaned_data:
                field_name = self.get_field_name()
                attribute_name = form.cleaned_data[field_name]
                if isinstance(attribute_name, str):
                    attribute_name = attribute_name.lower()
                if attribute_name in attribute_names:
                    raise ValidationError(
                        "Вы добавляете характеристику товара, которая уже существует, или создаете "
                        "несколько дублирующих характеристик"
                    )
                attribute_names.add(attribute_name)

    def get_field_name(self) -> str:
        return self.field_name
