from django.urls import path

from .views import ComparisonClearView, ComparisonRemoveView, ComparisonView

app_name = "comparison"

urlpatterns = [
    path("", ComparisonView.as_view(), name="service"),
    path("add/<int:pk>/", ComparisonView.as_view(), name="service_add"),
    path("remove/<int:pk>/", ComparisonRemoveView.as_view(), name="service_remove"),
    path("clear/", ComparisonClearView.as_view(), name="service_clear"),
]
