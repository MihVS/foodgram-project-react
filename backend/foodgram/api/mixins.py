from recipes.models import Recipe
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .serializers import ShortRecipesSerializer


class FavoriteShoppingcartMixin:
    """Вспомогательный класс для вьюсета."""

    def add_del_to_db(self, request, pk, related_model):
        """
        Добавляет и удаляет запись в БД рецепты избранные
        и в корзину для покупок.

        :param request: данные запроса.
        :param pk: id рецепта.
        :param related_model: Модель связанных данных.

        :return: Возвращает сериализованный объект и статус ответа.
        """

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        exists_in_db = related_model.objects.filter(
            user=user,
            recipe=recipe
        ).exists()

        if request.method == 'DELETE':
            if not exists_in_db:
                return Response(
                    {'errors': 'Рецепта не было в списке'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            related_model.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if exists_in_db:
            response = Response(
                {'errors': 'Этот рецепт уже был добавлен в избранное ранее'},
                status=status.HTTP_400_BAD_REQUEST
            )
            return response

        related_model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipesSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
