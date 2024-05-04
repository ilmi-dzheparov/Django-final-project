from django.urls import path
from .views import ProductListView, random_banners_view

app_name = "shop"


urlpatterns = [
    path("", ProductListView.as_view(), name="shop"),
    path('banners/', random_banners_view, name='banner'),
    ]
