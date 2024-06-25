from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator
from django.contrib.auth.models import BaseUserManager


def user_avatar_directory_path(instance: "User", filename: str):
    return 'accounts/avatar/user_{pk}/{filename}'.format(
        pk=instance.pk,
        filename=filename
    )


class User(AbstractUser):
    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет пользователя с заданным email и паролем.
        """
        if not email:
            raise ValueError('Пользователи должны иметь адрес электронной почты')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


    phone_regex = RegexValidator(regex=r'^((\+7)|8)\d{10}$', message='Phone number must be entered in the format: "+79999999999" or "89999999999" ')

    email = models.EmailField(unique=True)
    last_name = models.CharField(max_length=150, unique=False, blank=True, null=True)
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    middle_name = models.CharField(max_length=150, unique=False, blank=True, null=True)
    phone = models.CharField(max_length=12, unique=True, validators=[phone_regex], blank=True, null=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=user_avatar_directory_path)
    birth_date = models.DateField(null=True, blank=True)
    is_seller = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone']

    def get_full_name(self):
        return f"{self.last_name} {self.username} {self.middle_name}"

    def __str__(self) -> str:
        return f"User(pk={self.pk}, user={self.username})"
