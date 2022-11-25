from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import AmountIngredientRecipe, Ingredient, Recipe, Tag
from api.custom_fields import Base64ImageField


User = get_user_model()


class UsersSerializer(serializers.ModelSerializer):
    """
    Сериализатор для User.

    Поле is_subscribed вычисляется в методе get_is_subscribed.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'id',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        Проверяет подписку текущего пользователя на просматриваемого.

        :param obj: пользователь на которого проверяется подписка.
        :return: Если подписан, то возвращается True, иначе False.
        """

        user = self.context['request'].user

        if user.is_anonymous or (user == obj):
            return False

        return user.follower.filter(author=obj.id).exists()


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'id',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Создаёт нового пользователя с полученными полями.

        :param validated_data: полученные проверенные данные.
        :return: созданный пользователь.
        """
        return get_user_model().objects.create_user(**validated_data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientsForRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов рецепта.

    Выполнен через модель AmountIngredientRecipe
    """

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для рецепта."""

    author = UsersSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientsForRecipeSerializer(
        many=True, source='amount_ingredients'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        current_user = self.context.get('request').user
        print(validated_data)
        print(self.context)
        print(current_user)
        recipe = Recipe.objects.create(
            tags=3,
            author=current_user,
            name='test',
            image="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAg"
                  "MAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAA"
                  "AOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            text='TEST TEST',
            cooking_time=22
        )
        return recipe

    # def update(self, instance, validated_data):
    #     print('ya tut')
    #     return None

    # def create_ingredients(self, ingredients, recipe):
    #     for ingredient in ingredients:
    #         AmountIngredientRecipe.objects.create(
    #             recipe=recipe,
    #             ingredient_id=ingredient.get('id'),
    #             amount=ingredient.get('amount'),
    #         )
    #
    # def create(self, validated_data):
    #     image = validated_data.pop('image')
    #     ingredients_data = validated_data.pop('ingredients')
    #     recipe = Recipe.objects.create(image=image, **validated_data)
    #     tags_data = self.initial_data.get('tags')
    #     recipe.tags.set(tags_data)
    #     self.create_ingredients(ingredients_data, recipe)
    #     return recipe
