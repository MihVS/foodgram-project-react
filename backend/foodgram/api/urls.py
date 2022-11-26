from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, TagViewSet, RecipesViewSet)

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

]
