from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import User


# Автоматизированное создание пользователя с административными привилегиями с помощью сигнала post_migrate,
# который запускается после применения миграций
@receiver(post_migrate)
def create_admin_user(sender, **kwargs):
    if sender.name == 'app':
        User.objects.get_or_create(
            login='admin',
            defaults={
                'name': 'Admin',
                'admin': True,
                'password': 'admin#R4',
                'email': 'admin@admin.com'
            }
        )