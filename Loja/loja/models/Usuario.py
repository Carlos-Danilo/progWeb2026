from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from . import PERFIL


class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    perfil = models.IntegerField(choices=PERFIL, default=2)
    aniversario = models.DateField(default=None, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    alterado_em = models.DateTimeField(auto_now=True)
    token = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.user.username)


@receiver(post_save, sender=User)
def create_user_usuario(sender, instance, created, **kwargs):
    try:
        if created:
            Usuario.objects.create(user=instance)
    except:
        pass


@receiver(post_save, sender=User)
def save_user_usuario(sender, instance, **kwargs):
    try:
        instance.usuario.save()
    except:
        pass
