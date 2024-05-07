from django.urls import path
from shop.views import ProductDetailView

app_name = "shop"


urlpatterns = [
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail")
    ]
