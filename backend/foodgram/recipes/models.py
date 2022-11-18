from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=256,
        unique=True,
        verbose_name='Название',
    )
    color = models.CharField(
        max_length=16,
        unique=True,
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        unique=True,
    )


class Ingredients(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=10,
        verbose_name='Единицы измерения',
    )


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        # related_name='recipes',
        verbose_name='Тег',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название',
    )

