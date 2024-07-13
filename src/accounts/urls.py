from django.urls import path
from .views import (
    PersonalAccountView,
    ProfileView,
    CustomRegistrationView,
    login_view,
    UserLogoutView,
    send_password_reset_email_view,
    PasswordView,
    UserHistoryProductView,
    UserHistoryOrderView,
)

app_name = "accounts"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("email/", send_password_reset_email_view, name="email"),
    path("password_reset/<int:pk>/", PasswordView.as_view(), name="password_reset"),
    path("registration/", CustomRegistrationView.as_view(template_name="registration/registration_form.html"),
         name="registration"),
    path("account/<int:pk>/", PersonalAccountView.as_view(template_name="accounts/account.html"), name="account"),
    path("profile/<int:pk>/", ProfileView.as_view(template_name="accounts/profile.html"), name="profile"),
    path("history/product/", UserHistoryProductView.as_view(), name="product_viewing_history"),
    path("history/order/", UserHistoryOrderView.as_view(), name="history_of_orders"),

]
