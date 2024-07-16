from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(label='Username')
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот e-mail уже используется.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        username = self.cleaned_data.get('username')
        if password:
            user.set_password(password)
        user.username = username
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    full_name = forms.CharField(label='ФИО', required=False)
    email = forms.EmailField(label='Email', required=False)
    phone = forms.CharField(label='Телефон', required=False)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=False)
    avatar = forms.ImageField(label='Аватар', required=False)
    last_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    username = forms.CharField(widget=forms.HiddenInput(), required=False)
    middle_name = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'password', 'avatar', 'last_name', 'username', 'middle_name']

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
                raise forms.ValidationError("Пожалуйста, введите Фамилию, Имя и Отчество через пробел.")

        return cleaned_data

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Размер аватара не должен превышать 2MB.")
        return avatar

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class PasswordChangeForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['password']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


