from django.urls import path
from .views import PaymentProcess, PaymentCanceled

app_name = "payment"

urlpatterns = [
    path("payment-process/", PaymentProcess.as_view(), name="checkout"),
    path("payment-canceled/", PaymentCanceled.as_view(), name="canceled"),
]
