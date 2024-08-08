from django.urls import path

from .views import PaymentCanceled, PaymentProcess

app_name = "payment"

urlpatterns = [
    path("payment-process/<int:id>/", PaymentProcess.as_view(), name="checkout"),
    path("payment-canceled/", PaymentCanceled.as_view(), name="canceled"),
]
