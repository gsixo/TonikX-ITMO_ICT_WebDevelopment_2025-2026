from rest_framework import routers
from django.urls import path, include
from .views import StorageFundViewSet, CollectionViewSet, MuseumItemViewSet

router = routers.DefaultRouter()
router.register(r'funds', StorageFundViewSet, basename='fund')
router.register(r'collections', CollectionViewSet, basename='collection')
router.register(r'items', MuseumItemViewSet, basename='item')

urlpatterns = [
    path('', include(router.urls)),
]
