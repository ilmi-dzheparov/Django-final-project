from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Profile


@receiver(m2m_changed, sender=User.groups.through)
def update_user_seller_status(sender, instance, action, *args, **kwargs):
    if action in ['post_add', 'post_remove']:
        profile = Profile.objects.get(user=instance)
        profile.is_seller = instance.groups.filter(name='Seller').exists()
        profile.save()