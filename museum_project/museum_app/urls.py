from rest_framework import routers
from django.urls import path, include
from .views import (
    AddressViewSet,
    StorageFundViewSet,
    AuxiliaryCardIndexViewSet,
    CollectionViewSet,
    AuthorViewSet,
    MuseumItemViewSet,
    OrganizationViewSet,
    ExhibitionViewSet,
    ExhibitionParticipationViewSet,
    CollectionItemViewSet,
    MovementActViewSet,
    MovementViewSet,
)

router = routers.DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'funds', StorageFundViewSet, basename='fund')
router.register(r'auxiliary-indexes', AuxiliaryCardIndexViewSet, basename='aux-index')
router.register(r'collections', CollectionViewSet, basename='collection')
router.register(r'collection-items', CollectionItemViewSet, basename='collection-item')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'items', MuseumItemViewSet, basename='item')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'exhibitions', ExhibitionViewSet, basename='exhibition')
router.register(r'exhibition-participations', ExhibitionParticipationViewSet, basename='exhibition-participation')
router.register(r'movement-acts', MovementActViewSet, basename='movement-act')
router.register(r'movements', MovementViewSet, basename='movement')

urlpatterns = [
    path('', include(router.urls)),
]
