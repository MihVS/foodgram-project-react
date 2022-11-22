from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Тэги для рецептов"""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        unique=True,
    )

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """Ингредиенты для рецепта"""

    name = models.CharField(
        max_length=200,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт"""

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes_tags',
        verbose_name='Тег',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes_ingredients',
        verbose_name='Ингредиенты',

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
    image = models.ImageField(
        upload_to='recipes/',
    )
    description = models.TextField(
        verbose_name='Текст поста',
    )
    cooking_time = models.TimeField(
        verbose_name='Время приготовления',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pub_date']


class BaseList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s',
    )

    class Meta:
        abstract = True


class Favorite(BaseList):
    """Избранные рецепты пользователя"""

    pass


class SoppingCart(BaseList):
    """Список покупок пользователя"""

    pass


class Follow(models.Model):
    """Подписка на автора рецепта"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        blank=True,
        null=True
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        blank=True,
        null=True
    )
