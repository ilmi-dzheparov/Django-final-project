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


class UserUpdateForm(forms.ModelForm):
    last_name = forms.CharField(required=False)
    first_name = forms.CharField(required=False)
    middle_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)
    set_password = forms.CharField(required=False)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        last_name = cleaned_data.get('last_name')
        first_name = cleaned_data.get('first_name')
        middle_name = cleaned_data.get('middle_name')

        if not last_name or not first_name or not middle_name:
            raise forms.ValidationError("Пожалуйста, заполните хотя бы одно поле.")

        full_name = f"{last_name} {first_name} {middle_name}"
        cleaned_data['username'] = full_name
        return cleaned_data

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar', False)
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError('Размер файла должен быть не более 2 МБ')
        return avatar


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['email', 'password']
