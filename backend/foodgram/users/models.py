from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    USER_ROLES = (
        (ADMIN, 'Администратор'),
        (USER, 'Пользователь')
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=154,
        validators=[validate_username],
        unique=True
    )
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        max_length=254,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=30,
        choices=USER_ROLES,
        default='user'
    )

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def is_admin(self):
        return self.role == User.ADMIN or self.is_superuser

