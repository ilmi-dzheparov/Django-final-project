from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.views.generic import CreateView
from django.contrib import messages
from shop.models import Review
from shop.forms import ReviewForm


class ReviewCreateView(CreateView):
    """
    Представление: для создания отзыва к продукту.
    """

    model = Review
    form_class = ReviewForm

    def form_valid(self, form):
        review = form.save(commit=False)
        review.product_id = self.kwargs.get('pk')
        review.author = self.request.user
        review.save()
        return redirect(review.product.get_absolute_url())

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            #login_url = reverse('login')
            message = f"<p>Необходимо авторизоваться для добавления комментариев</p>"\
                      "<a href='{login_url}'>авторизоваться</a>"
            messages.info(request, mark_safe(message))
            return redirect(reverse(
                viewname='shop:product_detail',
                kwargs={'pk': self.kwargs.get('pk')}
            ))
        else:
            return super().dispatch(request, *args, **kwargs)