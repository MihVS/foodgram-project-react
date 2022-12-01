from django.contrib import admin

from .models import (AmountIngredientRecipe, Favorite, Follow, Ingredient,
                     Recipe, ShoppingCart, Tag)

admin.site.site_header = 'Администрирование Foodgram'
admin.site.index_title = 'Управление Foodgram'


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    """Настройки отображения рецептов в админке"""

    list_display = (
        'id',
        'name',
        'author',
        'text',
        'cooking_time',
        'image',
        'pub_date',
        'in_favorite'
    )
    list_display_links = ('name',)
    list_filter = ('tags', 'author', 'name')
    search_fields = ('name', 'author__username', 'tags__slug')
    list_per_page = 20

    def in_favorite(self, obj):
        """
        Вычисляет количество добавлений рецепта в избранное.

        :param obj: Объект рецепта.
        :return: Количество рецепта в избранном у всех пользователей.
        """

        return len(Favorite.objects.filter(recipe=obj.id))

    in_favorite.short_description = 'В избранном'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки отображения ингредиентов в админке"""

    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    list_per_page = 20


@admin.register(AmountIngredientRecipe)
class AmountIngredientRecipeAdmin(admin.ModelAdmin):
    """Настройки отображения количества ингредиентов в админке"""

    list_display = ('id', 'amount', 'ingredient', 'recipe')
    list_editable = ('amount',)
    search_fields = ('ingredient__name', 'recipe__name')
    list_per_page = 20


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Настройки отображения избранного в админке"""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_per_page = 20


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройки отображения корзин покупок пользователей в админке"""

    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_per_page = 20


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Настройки отображения подписок пользователей в админке"""

    list_display = ('id', 'user', 'author')
    search_fields = ('user__username', 'author__username')
    list_per_page = 20


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки отображения тегов в админке"""

    list_display = ('id', 'color', 'name', 'slug')
