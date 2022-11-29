from rest_framework import viewsets, permissions, status
from django.contrib.auth import get_user_model

from rest_framework.generics import get_object_or_404

from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import (IngredientSerializer, RecipesSerializer,
                          UsersSerializer, TagSerializer, FollowSerializer)

from recipes.models import (Ingredient, Recipe, Tag, Follow, Favorite,
                            ShoppingCart)

from .mixins import FavoriteShoppingcartMixin


User = get_user_model()


class UsersViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователей"""

    queryset = User.objects.all()
    serializer_class = UsersSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, pk):
        """
        Создаётся или удаляется подписка на пользователя.

        :param request: данные запроса.
        :param pk: id пользователя на которого нужно подписаться(отписаться).
        :return:
        """

        user = request.user
        author = get_object_or_404(User, id=pk)
        is_subscribed = Follow.objects.filter(
            user=user,
            author=author
        ).exists()

        if request.method == 'DELETE':
            if not is_subscribed:
                response = Response(
                    {'errors': 'Вы не были подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                return response

            Follow.objects.get(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if user == author:
            response = Response(
                {'errors': 'Подписка самого на себя невозможна'},
                status=status.HTTP_400_BAD_REQUEST
            )
            return response

        if is_subscribed:
            response = Response(
                {'errors': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
            return response

        Follow.objects.create(user=user, author=author)

        follow = User.objects.get(pk=author.id)
        serializer = FollowSerializer(
            follow,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        """
        Получаем всех пользователей на которых подписан.

        :param request: данные запроса.
        :return: Возвращает сериализованные данные через FollowSerializer
                 с пагинацией.
        """

        user = request.user
        queryset = User.objects.filter(following__user_id=user.id)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для тегов.

    Теги доступны только для чтения.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для ингредиентов.

    Теги доступны только для чтения.
    """

    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        """
        Получает queryset в соответствии параметром name.

        Поиск по частичному вхождению в начале названия ингредиента.
        """

        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')

        if name:
            queryset = queryset.filter(name__istartswith=name)

        return queryset


class RecipesViewSet(viewsets.ModelViewSet, FavoriteShoppingcartMixin):
    """Вьюсет для рецептов"""

    queryset = Recipe.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk):
        """
        Добавляет(удаляет) рецепт в избранное пользователя.

        :param pk: id добавляемого рецепта.
        :param request: данные запроса.
        :return: Возвращает сериализованный рецепт который добавили
                 или удалили из избранного.
        """
        response = self.add_del_to_db(
            request=request,
            pk=pk,
            related_model=Favorite
        )
        return response

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        """
        Добавляет(удаляет) рецепт в корзину для покупок.

        :param pk: id добавляемого рецепта.
        :param request: данные запроса.
        :return: Возвращает сериализованный рецепт, который добавили
                 или удалили в корзину для покупок.
        """

        response = self.add_del_to_db(
            request=request,
            pk=pk,
            related_model=ShoppingCart
        )
        return response

    @action(methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def download_shopping_cart(self, request):
        """
        Формирует файл списка продуктов из рецептов в списке покупок.

        :param request:
        :return:
        """
        return None
