from django.contrib.auth import get_user_model
from django.db.models import Sum, F
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from recipes.models import (Ingredient, Recipe, Tag, Follow, Favorite,
                            ShoppingCart, AmountIngredientRecipe)
from .filters import IngredientFilter, RecipeFilter
from .mixins import FavoriteShoppingcartMixin
from .permissions import IsOwnerAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipesSerializer,
                          TagSerializer, FollowSerializer)

User = get_user_model()


class UsersViewSet(DjoserUserViewSet):
    """Вьюсет для пользователей"""

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
        methods=['get'],
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

    queryset = Ingredient.objects.all()

    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipesViewSet(viewsets.ModelViewSet, FavoriteShoppingcartMixin):
    """Вьюсет для рецептов"""

    queryset = Recipe.objects.all()
    serializer_class = RecipesSerializer
    permission_classes = (IsOwnerAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsOwnerAdminOrReadOnly],
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
        permission_classes=[IsOwnerAdminOrReadOnly],
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

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsOwnerAdminOrReadOnly],
    )
    def download_shopping_cart(self, request):
        """
        Формирует файл списка продуктов из рецептов в списке покупок.

        :param request:
        :return:
        """

        user = request.user

        if user.is_anonymous:
            raise permissions.exceptions.AuthenticationFailed

        if not user.shoppingcart.all().exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        recipes_of_user = user.shoppingcart.values('recipe')
        ingredients_in_recipes = AmountIngredientRecipe.objects.filter(
            recipe__in=recipes_of_user
        )
        sum_ingredients = ingredients_in_recipes.values(
            ingredient_name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount'))

        list_ingredients = (f'Список продуктов для пользователя с именем: '
                            f'{user.get_full_name()}\n\n')

        for ingredient in sum_ingredients:
            ingredient_str = (f'{ingredient["ingredient_name"]} '
                              f'({ingredient["measurement_unit"]}) - '
                              f'{ingredient["amount"]}\n')
            list_ingredients += ingredient_str

        file_name = f'shopping_cart_{user.username}.txt'
        response = HttpResponse(
            content=list_ingredients,
            content_type='text/plain; charset=utf-8',
            status=status.HTTP_200_OK,
        )
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response
