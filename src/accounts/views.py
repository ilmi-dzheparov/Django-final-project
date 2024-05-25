from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django_registration.backends.activation.views import RegistrationView
from .forms import UserRegisterForm, UpdateProfileForm


class CustomRegistrationView(RegistrationView):
    form_class = UserRegisterForm
    template_name = 'registration/registration_form.html'

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
    template_name = 'profile.html'
    success_url = reverse_lazy('accounts:profile')
    form = UpdateProfileForm
    fields = ['username', 'email', 'phone', 'password', 'avatar']




