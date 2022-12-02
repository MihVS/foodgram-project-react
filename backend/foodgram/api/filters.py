from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    """Класс для настройки фильтра рецептов"""

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(
        field_name='favorite',
        method='filter_is_list'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='shoppingcart',
        method='filter_is_list'
    )

    class Meta:
        model = Recipe
        fields = [
            'is_favorited',
            'author',
            'is_in_shopping_cart',
            'tags'
        ]

    def filter_is_list(self, queryset, name, value):
        """
        Фильтрует вывод по наличию в списке избранного или корзине.

        :param queryset: Кверисет рецептов.
        :param name: Имя поля.
        :param value: Переданное значение фильтра.
        :return: Возвращает отфильтрованный кверисет.
        """

        if not value:
            return queryset
        lookup = '__'.join([name, 'user'])
        return queryset.filter(**{lookup: self.request.user.id})


class IngredientFilter(filters.FilterSet):
    """Класс для настройки фильтра ингредиентов"""

    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
