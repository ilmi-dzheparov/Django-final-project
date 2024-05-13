from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import User


@receiver(m2m_changed, sender=User.groups.through)
def update_user_seller_status(sender, instance, action, *args, **kwargs):
    if action in ['post_add', 'post_remove']:
        instance.is_seller = instance.groups.filter(name='Seller').exists()
        instance.save()
