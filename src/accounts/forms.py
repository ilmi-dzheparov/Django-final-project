from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserRegisterForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Enter Password Again', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'phone')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('Такой email уже используется в системе')
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            "placeholder": "Пароль",
            'name': "pass",
            'id': "name",
        })
        self.fields['password2'].widget.attrs.update({
            "placeholder": "Повторите пароль"
        })
        self.fields['email'].widget.attrs.update({
            'name': "login",
            'id': "name",
            'placeholder': 'E-mail',
            'class': 'user-input'
        })

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UpdateProfileForm(forms.ModelForm):
    last_name = forms.CharField(required=True)
    first_name = forms.CharField(required=True)
    middle_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'middle_name', 'email', 'phone', 'password', 'avatar')

    def update_profile(self, new_info):
        errors = self.validate_profile(new_info)
        if errors:
            for field, error in errors.items():
                print(f"Ошибка в поле {field}: {error}")
        else:
            new_info.pop('csrfmiddlewaretoken', None)  # Remove CSRF token if present
            full_name = f"{new_info.get('last_name')} {new_info.get('first_name')} {new_info.get('middle_name')}"
            self.instance.username = full_name
            self.instance.email = new_info.get('email')
            self.instance.phone = new_info.get('phone')
            self.instance.set_password(new_info.get('password'))
            self.instance.avatar = new_info.get('avatar')
            self.instance.save()
            print("Профиль успешно обновлен")

    # Валидация введенных данных и их уникальность
    def validate_profile(self, new_info):
        errors = {}
        if User.objects.filter(email=new_info.get('email')).exclude(pk=self.instance.pk).exists():
            errors['Email'] = "Данный email уже используется"
        if User.objects.filter(phone=new_info.get('phone')).exclude(pk=self.instance.pk).exists():
            errors['Телефон'] = "Данный телефон уже используется"

        # Проверка размера фотографии
        if new_info.get('avatar') and len(new_info['avatar']) > 2 * 1024 * 1024:
            errors['Аватарка'] = "Размер аватарки должен быть не более 2 Мб"

        return errors


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['email', 'password']
