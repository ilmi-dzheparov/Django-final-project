from django.contrib.auth.views import LoginView, PasswordResetView
from django_registration.views import RegistrationView
from django.urls import path

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("reset/", PasswordResetView.as_view(template_name="registration/password_reset.html")),
    path("registration/", RegistrationView.as_view(template_name="registration/registration_form.html")),
]
