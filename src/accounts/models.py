from django.db import models
from django.contrib.auth.models import User


def profile_avatar_directory_path(instance: "Profile", filename: str):
    return 'accounts/avatar/user_{pk}/{filename}'.format(
        pk=instance.user.pk,
        filename=filename
    )


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10)
    avatar = models.ImageField(null=True, blank=True, upload_to=profile_avatar_directory_path)
    created_at = models.DateField(auto_now_add=True)
    birth_date = models.DateField(null=True, blank=True)
    is_seller = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Profile(pk={self.pk}, user={self.user!r})"
