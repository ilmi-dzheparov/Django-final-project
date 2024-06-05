from django import forms
from django.core.exceptions import ValidationError


class UserDataForm(forms.Form):
    full_name = forms.CharField(
        label='Full Name',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Иванов Иван Иванович'})
    )
    phone = forms.CharField(
        label='Phone',
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7 (___) ___-__-__'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )


class PasswordForm(forms.Form):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )
    password2 = forms.CharField(
        label='Enter Password Again',
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )

    def clean_password2(self):

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2


class SelectDeliveryForm(forms.Form):
    DELIVERY_CHOICES = [
        ('regular', 'Обычная доставка'),
        ('express', 'Экспресс доставка'),
    ]

    delivery_option = forms.ChoiceField(choices=DELIVERY_CHOICES, widget=forms.RadioSelect())
    city = forms.CharField(label='Город', max_length=100)
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-textarea'}))


class SelectPaymentForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Онлайн картой'),
        ('account', 'Онлайн со случайного чужого счета'),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect()
    )
