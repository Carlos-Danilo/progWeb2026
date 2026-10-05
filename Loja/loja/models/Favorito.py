from django.conf import settings
from django.db import models

from .Produto import Produto


class Favorito(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='produtos_favoritos',
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='favoritos',
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'produto'],
                name='unique_user_favorite_product',
            ),
        ]

    def __str__(self):
        return f'{self.user}: {self.produto}'
