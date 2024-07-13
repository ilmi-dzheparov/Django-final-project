from django.urls import path

from .views import DiscountListView, ProductDiscountDetailView, BundleDiscountDetailView, CartDiscountDetailView

app_name = "discounts"

urlpatterns = [
    path('discounts/', DiscountListView.as_view(), name='discount-list'),
    path('discounts/product_discount/<int:pk>/', ProductDiscountDetailView.as_view(), name='product-discount-detail'),
    path('discounts/bundle_discount/<int:pk>/', BundleDiscountDetailView.as_view(), name='bundle-discount-detail'),
    path('discounts/cart_discount/<int:pk>/', CartDiscountDetailView.as_view(), name='cart-discount-detail'),
]
