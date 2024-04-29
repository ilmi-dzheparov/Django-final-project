from django.urls import path
from .views import (
    ProductListView,
    ReviewCreateView,
)

app_name = "shop"


urlpatterns = [
    path("", ProductListView.as_view(), name="shop"),
    path('product/<int:pk>/review/create/', ReviewCreateView.as_view(), name='review_create'),
    ]
