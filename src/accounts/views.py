import os
import smtplib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.views import LogoutView
from django.core.mail import send_mail, get_connection
from django.http import HttpRequest, request
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, DetailView, CreateView, ListView, View
from orders.models import Order
from .models import User
from shop.models import HistoryProduct
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UserRegisterForm, UserUpdateForm, PasswordChangeForm


def login_view(request: HttpRequest):
    if request.method == "GET":
        return render(request, 'registration/login.html')

    email = request.POST.get("email")
    password = request.POST.get("password")

    if not email:
        return render(request, 'registration/login.html', {"error": "Необходимо ввести электронную почту"})

    if not password:
        return render(request, 'registration/login.html', {"error": "Необходимо ввести пароль"})

    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        return redirect("accounts:account", pk=user.pk)

    return render(request, 'registration/login.html', {"error": "Не получилось войти, проверьте логин или пароль"})


class CustomRegistrationView(CreateView):
    model = User
    template_name = 'accounts/registration_form.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class PersonalAccountView(LoginRequiredMixin, DetailView):
    """
    Свободная страница личного кабинета, на которой отображаются данные о пользователе:
    """
    template_name = 'accounts/account.html'
    success_url = reverse_lazy("accounts:account")
    model = User
    context_object_name = 'user'


class ProfileView(UpdateView):
    model = User
    template_name = 'accounts/profile.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy("accounts:profile")

    def get_success_url(self):
        return reverse_lazy('accounts:account', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class UserHistoryView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        history = HistoryProduct.objects.filter(user=user)[:20]
        return render(request, template_name="includes/history-product.html",
                      context={"recently_viewed_products": history})


def send_password_reset_email(user):
    subject = 'Сброс пароля'
    password_reset_link = f"{os.getenv('DOMEN_APP')}{reverse('accounts:password_reset', kwargs={'pk': user.pk})}"

    message = (f'Здравствуйте, это сообщение пришло вам, так как вы запросили сброс пароля.'
               f' Если это не вы, можете не реагировать на это сообщение. Для изменения пароля перейдите по ссылке.\n'
               f'\nСсылка для сброса пароля: {password_reset_link}')
    email_from = os.getenv('EMAIL_HOST_USER')
    recipient_list = [user.email]

    smtp_connection = get_connection()
    smtp_connection.open()

    try:
        send_mail(subject, message, email_from, recipient_list, fail_silently=False, connection=smtp_connection)
    except smtplib.SMTPException as e:
        print(f'An error occurred: {e}')

    smtp_connection.close()


def send_password_reset_email_view(request):
    message = None

    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(user)
            message = "Письмо успешно отправлено, перейдите по ссылке в письме для сброса пароля."
        except User.DoesNotExist:
            message = "Пользователь не найден."

    return render(request, 'registration/email.html', {'message': message})


class PasswordView(UpdateView):
    model = User
    template_name = 'registration/password_reset.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy("accounts:password_reset")

    def get_success_url(self):
        return reverse_lazy('accounts:logout')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class UserHistoryProductView(View):
    """
    Представление для отображения списка просмотренных товаров.
    """

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = request.user.pk
        history = HistoryProduct.objects.filter(user=user)[:8]
        return render(request, template_name="accounts/history-product.html",
                      context={"recently_viewed_products": history})


class UserHistoryOrderView(ListView):
    """
    Представление для отображения списка заказов пользователя.
    """

    template_name = 'accounts/history-order.html'
    model = Order
    context_object_name = 'orders'

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(user=user).order_by('-created_at')
        return queryset
