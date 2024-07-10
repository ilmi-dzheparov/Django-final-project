from django.urls import path

from .views import DiscountListView, DiscountDetailView


urlpatterns = [
    path('discounts/', DiscountListView.as_view(), name='discount-list'),
    path('discounts/int:pk/', DiscountDetailView.as_view(), name='discount-detail'),
]
