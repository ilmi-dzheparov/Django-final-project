from django import forms
from django.core.exceptions import ValidationError
from accounts.models import User


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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserDataForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and self.user.is_authenticated:
            return email

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует. Вы можете войти.")

        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if self.user and self.user.is_authenticated:
            return phone

        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Пользователь с таким телефоном уже существует.")

        return phone

    def clean(self):
        cleaned_data = super().clean()

        full_name = cleaned_data.get('full_name')

        if full_name:
            names = full_name.split()
            if len(names) == 3:
                cleaned_data['last_name'] = names[0]
                cleaned_data['username'] = names[1]
                cleaned_data['middle_name'] = names[2]
            else:
                raise ValidationError("Пожалуйста, введите Фамилию, Имя и Отчество через пробел.")

        return cleaned_data


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

    delivery_method = forms.ChoiceField(choices=DELIVERY_CHOICES, widget=forms.RadioSelect())
    city = forms.CharField(max_length=100)
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-textarea'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delivery_method'].label = False


class SelectPaymentForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Онлайн картой'),
        ('account', 'Онлайн со счета'),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].label = False


class CommentOrderForm(forms.Form):
    comment = forms.CharField(max_length=255, required=False)
