from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

def profile_avatar_directory_path(instance: "Profile", filename: str):
    return 'accounts/avatar/user_{pk}/{filename}'.format(
        pk=instance.user.pk,
        filename=filename
    )


class User(AbstractUser):

    phone_regex = RegexValidator(regex=r'^((\+7)|8)/d{10}$', message='Phone number must be entered in the format: "+79999999999" or "89999999999" ')

    phone = models.CharField(max_length=12, unique=True, validators=[phone_regex])
    avatar = models.ImageField(null=True, blank=True, upload_to=profile_avatar_directory_path)
    created_at = models.DateField(auto_now_add=True)
    birth_date = models.DateField(null=True, blank=True)
    is_seller = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"User(pk={self.pk}, user={self.username})"
