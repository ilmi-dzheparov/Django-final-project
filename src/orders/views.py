from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.urls import reverse, reverse_lazy
from accounts.models import User
from .forms import (
    UserDataForm,
    PasswordForm,
    SelectDeliveryForm,
    SelectPaymentForm
)


class Step1UserData(FormView):
    template_name = 'orders/step1-user-data.html'
    form_class = UserDataForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            context['password_form'] = PasswordForm()
        context['current_step'] = 'step1'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.user.is_authenticated:
            kwargs['initial'] = {
                'full_name': self.request.user.first_name,
                'phone': self.request.user.phone,
                'email': self.request.user.email,
            }
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            success_url = reverse('orders:delivery')
            return redirect(success_url)
        else:
            password = form.cleaned_data.get('password2')
            email = form.cleaned_data.get('email')
            full_name = form.cleaned_data.get('full_name')
            phone = form.cleaned_data.get('phone')

            # Создание нового пользователя с введенным данными из формы.
            user = User.objects.create_user(
                full_name=full_name,
                email=email,
                password=password,
                phone=phone
            )
            login(self.request, user)
            success_url = reverse('orders:delivery')
            return redirect(success_url)


class Step2SelectDelivery(FormView):
    template_name = 'orders/step2-select-delivery.html'
    form_class = SelectDeliveryForm
    success_url = reverse_lazy('orders:payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_step'] = 'step2'
        return context

    def form_valid(self, form):
        return super().form_valid(form)


class Step3SelectPayment(FormView):
    template_name = 'orders/step3-select-payment.html'
    form_class = SelectPaymentForm
    success_url = 'orders:confirmation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_step'] = 'step3'
        return context

    def form_valid(self, form):
        return super().form_valid(form)


class Step4OrderConfirmation(FormView):
    pass
