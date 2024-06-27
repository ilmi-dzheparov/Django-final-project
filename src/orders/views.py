from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, DetailView
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from orders.models import Order
from shop.models import CartItem, Cart, SellerProduct
from accounts.models import User
from orders.forms import (
    UserDataForm,
    PasswordForm,
    SelectDeliveryForm,
    SelectPaymentForm,
    CommentOrderForm
)


class Step1UserData(FormView):
    """
    Шаг 1. Оформление заказа. Ввод данных пользователя.
    Для авторизованного пользователя данные из профиля подставляются из базы данных.
    Для не авторизованного пользователя можно ввести данные с паролем в форму и попробовать
    зарегистрироваться, после чего продолжить оформление заказа.
    После успешной валидации данных идет перенаправление на следующий шаг (выбор доставки).
    """

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
        user = self.request.user
        if user.is_authenticated:
            kwargs['initial'] = {
                'full_name': user.get_full_name,
                'phone': user.phone,
                'email': user.email,

            }
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            success_url = reverse('orders:select_delivery')
            return redirect(success_url)
        else:
            password = form.cleaned_data.get('password2')
            email = form.cleaned_data.get('email')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            middle_name = form.cleaned_data.get('middle_name')
            phone = form.cleaned_data.get('phone')

            # Создание нового пользователя с введенным данными из формы.
            user = User.objects.create_user(
                last_name=last_name,
                username=username,
                middle_name=middle_name,
                email=email,
                password=password,
                phone=phone
            )
            login(self.request, user)
            success_url = reverse('orders:select_delivery')

            return redirect(success_url)


class Step2SelectDelivery(FormView):
    """
    Шаг 2. Оформление заказа. Выбор доставки.
    В форме выбирается обычная или экспресс доставка, так-же вводится город и адрес доставки.
    После успешной валидации данных идет перенаправление на следующий шаг (выбор оплаты).
    """

    template_name = 'orders/step2-select-delivery.html'
    form_class = SelectDeliveryForm
    success_url = reverse_lazy('orders:select_payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_step'] = 'step2'

        return context

    def form_valid(self, form):
        delivery_method = form.cleaned_data['delivery_method']
        choices_delivery = dict(SelectDeliveryForm.DELIVERY_CHOICES)
        delivery_method_description = choices_delivery.get(delivery_method)
        city = form.cleaned_data['city']
        address = form.cleaned_data['address']
        order_data = cache.get('order_data', {})
        order_data.update({
            'delivery_method': delivery_method_description,
            'city': city,
            'address': address,
        })
        cache.set('order_data', order_data)

        return super().form_valid(form)


class Step3SelectPayment(FormView):
    """
    Шаг 3. Оформление заказа. Выбор оплаты.
    Выбирается один из вариантов: «Онлайн картой», «Онлайн со случайного чужого счёта».
    После успешной валидации данных идет перенаправление на следующий шаг (подтверждение заказа).
    """

    template_name = 'orders/step3-select-payment.html'
    form_class = SelectPaymentForm
    success_url = reverse_lazy('orders:confirmation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_step'] = 'step3'

        return context

    def form_valid(self, form):
        payment_method = form.cleaned_data['payment_method']
        choices_payment = dict(SelectPaymentForm.PAYMENT_METHOD_CHOICES)
        payment_method_description = choices_payment.get(payment_method)
        order_data = cache.get('order_data', {})
        order_data['payment_method'] = payment_method_description
        cache.set('order_data', order_data, None)

        return super().form_valid(form)


class Step4OrderConfirmation(FormView):
    """
    Шаг 4. Оформление заказа. Подтверждение заказа.
    В данном представлении выводятся все данные заказа
    """

    template_name = 'orders/step4-order_confirmation.html'
    form_class = CommentOrderForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(pk=self.request.user.pk)

        # Получаем корзину пользователя
        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)
        total_price = cart.total_price()
        order_data = cache.get('order_data', {})
        context['order'] = order_data
        context['cart_items'] = cart_items
        context['total_price'] = total_price
        context['user'] = user
        context['form_comment'] = CommentOrderForm()
        context['current_step'] = 'step4'

        return context

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        user = User.objects.get(pk=self.request.user.pk)
        order_data = cache.get('order_data', {})
        delivery_method = order_data.get('delivery_method')
        city = order_data.get('city')
        address = order_data.get('address')
        payment_method = order_data.get('payment_method')
        comment = form.cleaned_data['comment']

        order, created = Order.objects.get_or_create(
            user=user,
            delivery_method=delivery_method,
            payment_method=payment_method,
            city=city,
            address=address,
            comment=comment,
        )

        # Добавление товаров в заказ

        cart = Cart.objects.get(user=user)
        cart_items = CartItem.objects.filter(cart=cart)

        for cart_item in cart_items:
            product = SellerProduct.objects.get(pk=cart_item.product.pk)
            order.seller_product.add(product)
            order.save()

        if payment_method == 'Онлайн картой':
            return render(self.request, template_name='orders/payment-by-card.html')
        elif payment_method == 'Онлайн со счета':
            return render(self.request, template_name='orders/payment-from-account.html')
        else:
            messages.error(self.request, "Способ оплаты не установлен.")
            return HttpResponseRedirect(reverse('orders:confirmation'))


class OrderDetail(DetailView):
    model = Order
    template_name = 'orders/oneorder.html'
    context_object_name = 'order'

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(user=user)
        return queryset

    def get_object(self, queryset=None):
        order_id = self.kwargs.get('pk')
        order = get_object_or_404(Order, pk=order_id, user=self.request.user)
        return order
