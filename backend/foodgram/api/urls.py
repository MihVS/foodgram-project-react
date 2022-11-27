from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, TagViewSet, RecipesViewSet,
                       UsersViewSet)

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')
router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    # path('users/subscriptions/', FollowerViewSet.as_view(
    #     {'get': 'list'}
    # )),
    # path('users/<int:pk>/subscriptions/', FollowerViewSet.as_view(
    #     {'post': 'create', 'delete': 'destroy'}
    # )),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
