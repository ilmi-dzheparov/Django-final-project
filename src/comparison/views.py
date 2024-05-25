from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from .comparison import Comparison
from django.urls import reverse
from django.views import View


@method_decorator(decorator=never_cache, name="get")
class ComparisonView(View):
    def get(self, request, *args, **kwargs):
        service = Comparison(request)

        # получаем контекст сервиса
        context = service.service_context()
        context["service"] = service
        return render(request=request, template_name="shop/comparison.html", context=context)

    def post(self, request, pk, *args, **kwargs):
        service = Comparison(request)
        service.add(product_pk=pk)

        return redirect(reverse("comparison:service"))


class ComparisonRemoveView(View):
    def post(self, request, pk, *args, **kwargs):
        service = Comparison(request)
        service.remove(product_pk=pk)
        return redirect(reverse("comparison:service"))


class ComparisonClearView(View):
    def post(self, request, *args, **kwargs):
        service = Comparison(request)
        service.clear()

        return redirect(reverse("comparison:service"))
