from django.urls import path
from shop.views import ProductDetailView, ReviewCreateView

app_name = "shop"


urlpatterns = [
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path('product/<int:pk>/review/create/', ReviewCreateView.as_view(), name='review_create'),
    ]
