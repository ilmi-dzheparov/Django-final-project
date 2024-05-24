from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django_registration.backends.activation.views import RegistrationView
from .forms import UserRegisterForm


class CustomRegistrationView(RegistrationView):
    form_class = UserRegisterForm

    def get_success_url(self, user=None):
        return reverse_lazy("accounts:account")


class PersonalAccountView(LoginRequiredMixin, View):
    """
    Свободная страница личного кабинета, на которой отображаются данные о пользователе:
    """
    template_name = 'accounts/account.html'
    success_url = reverse_lazy("accounts:account")
    model = User

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        context = {
            'user': user
        }
        return render(request, self.template_name, context)


class ProfileView(UpdateView):
    model = User
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('accounts:profile')
    fields = ['username', 'email', 'phone', 'password', 'avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def update_profile(self, new_info):
        errors = self.validate_profile(new_info)
        if errors:
            for field, error in errors.items():
                print(f"Ошибка в поле {field}: {error}")
        else:
            new_info.pop('csrfmiddlewaretoken', None)  # Убираем CSRF токен, если есть
            self.object.full_name = new_info.get('username')
            self.object.email = new_info.get('email')
            self.object.phone = new_info.get('phone')
            self.object.set_password(new_info.get('password'))
            self.object.avatar = new_info.get('avatar')
            self.object.save()
            print("Профиль успешно обновлен")

    def validate_profile(self, new_info):
        errors = {}
        if not new_info.get('full_name'):
            errors['Ф. И. О.'] = "Поле обязательно для заполнения"
        if not new_info.get('email'):
            errors['Email'] = "Поле обязательно для заполнения"
        if User.objects.filter(email=new_info.get('email')).exists():
            errors['Email'] = "Данный email уже используется"
        if User.objects.filter(phone=new_info.get('phone')).exists():
            errors['Телефон'] = "Данный телефон уже используется"

        # Проверяем размер аватарки
        if new_info.get('avatar') and len(new_info['avatar']) > 2 * 1024 * 1024:
            errors['Аватарка'] = "Размер аватарки должен быть не более 2 Мб"

        return errors


