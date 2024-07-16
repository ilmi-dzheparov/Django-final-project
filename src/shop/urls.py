from django.urls import path
from .views import (
    ProductDetailView,
    ReviewCreateView,
    AddToCartView,
    CartDetailView,
    CartItemDeleteView,
    CartItemUpdateView,
    IndexView,
    Catalog,
    CatalogProduct
)

app_name = "shop"

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product_detail"),
    path('product/<int:pk>/review/create/', ReviewCreateView.as_view(), name='review_create'),
    path('cart/<int:pk>/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', CartDetailView.as_view(), name='cart_detail'),
    path('cart/item/<int:pk>/delete/', CartItemDeleteView.as_view(), name='cart_delete'),
    path('cart/item/<int:pk>/update/', CartItemUpdateView.as_view(), name='cart_update'),
    path('catalog/', Catalog.as_view(), name='product_list'),
    path('catalog/<int:pk>/', CatalogProduct.as_view(), name='catalog_products_list'),
]
