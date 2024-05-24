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
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['email', 'password']
