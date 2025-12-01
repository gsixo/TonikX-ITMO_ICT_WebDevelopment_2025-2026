from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Address,
    StorageFund,
    AuxiliaryCardIndex,
    Collection,
    Author,
    MuseumItem,
    Organization,
    Exhibition,
    ExhibitionParticipation,
    CollectionItem,
    MovementAct,
    Movement,
)
from .serializers import (
    AddressSerializer,
    StorageFundSerializer,
    AuxiliaryCardIndexSerializer,
    CollectionSerializer,
    AuthorSerializer,
    MuseumItemSerializer,
    OrganizationSerializer,
    ExhibitionSerializer,
    ExhibitionParticipationSerializer,
    CollectionItemSerializer,
    MovementActSerializer,
    MovementSerializer,
)
from . import services


"""
Views module for museum_app.

All class and method docstrings are written in Google style so mkdocstrings
can render them automatically into your MkDocs site.
"""


class AddressViewSet(viewsets.ModelViewSet):
    """
    CRUD for addresses used by funds, organizations and exhibitions.
    """

    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class StorageFundViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StorageFund management.

    Provides read-only CRUD for storage funds and a couple of report endpoints.

    Endpoints:
        - GET /api/funds/                      List all funds.
        - GET /api/funds/{id}/                 Retrieve a fund by id.
        - GET /api/funds/exhibitions_count/    For each fund: number of unique exhibitions.
        - GET /api/funds/full_report/          Full funds report (items + first receive date + exhibition counts).

    Attributes:
        queryset (QuerySet): Base queryset for the viewset.
        serializer_class (Serializer): Serializer used for representation.
    """
    queryset = StorageFund.objects.all()
    serializer_class = StorageFundSerializer

    @action(detail=False, methods=['get'])
    def exhibitions_count(self, request):
        """
        Return number of unique exhibitions for each fund.

        Returns:
            rest_framework.response.Response: JSON array of objects with fields:
                - id (int): fund id
                - name (str): fund name
                - exhibitions_count (int): number of unique exhibitions containing items from this fund

        Example:
            GET /api/funds/exhibitions_count/

            Response:
            [
              {"id": 1, "name": "Живопись", "exhibitions_count": 12},
              {"id": 2, "name": "Графика", "exhibitions_count": 5}
            ]
        """
        data = services.get_funds_exhibitions_count()
        return Response(data)

    @action(detail=False, methods=['get'])
    def full_report(self, request):
        """
        Return full report across all funds.

        For each fund returns:
         - fund_id, fund_name
         - items_count (int)
         - items: list of items with fields:
             - inventory_number
             - name
             - first_receive_date (date|null)
             - exhibitions_count (int)
             - is_written_off (bool)

        Returns:
            rest_framework.response.Response: dict with keys 'total_items' and 'funds'.

        Example:
            GET /api/funds/full_report/

            Response:
            {
              "total_items": 120,
              "funds": [
                {
                  "fund_id": 1,
                  "fund_name": "Живопись",
                  "items_count": 40,
                  "items": [
                    {
                      "inventory_number": "A-001",
                      "name": "Картина 1",
                      "first_receive_date": "2020-01-05",
                      "exhibitions_count": 3,
                      "is_written_off": false
                    },
                    ...
                  ]
                },
                ...
              ]
            }
        """
        data = services.get_full_funds_report()
        return Response(data)


class CollectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Collections (sets / комплекты).

    Endpoints:
      - GET /api/collections/                 List collections
      - GET /api/collections/{id}/            Retrieve collection
      - GET /api/collections/{id}/items_count/  Number of items in the collection

    Attributes:
        queryset (QuerySet): Base queryset for the viewset.
        serializer_class (Serializer): Serializer used for representation.
    """
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    @action(detail=True, methods=['get'])
    def items_count(self, request, pk=None):
        """
        Return the number of items in the requested collection.

        Args:
            pk (int): Primary key of the collection.

        Returns:
            rest_framework.response.Response: JSON object with 'id', 'name', 'items_count'.

        Example:
            GET /api/collections/5/items_count/

            Response:
            {"id": 5, "name": "Сервиз X", "items_count": 12}
        """
        count_data = services.get_collections_items_count()
        for c in count_data:
            if c['id'] == int(pk):
                return Response(c)
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class MuseumItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MuseumItem (карточки музейных предметов).

    Provides CRUD and several report endpoints specific to items.

    Endpoints:
      - GET /api/items/                          List items
      - POST /api/items/                         Create item
      - GET /api/items/{id}/                     Retrieve item
      - PATCH /api/items/{id}/                   Partial update
      - DELETE /api/items/{id}/                  Delete item
      - GET /api/items/{id}/related_by_exhibitions/  Other items in same exhibitions
      - GET /api/items/written_off_count_by_fund/?from=YYYY-MM-DD&to=YYYY-MM-DD
                                                Count of written-off items per fund in a period
      - GET /api/items/fund_volume_percentage/   Percentage share of each fund by item count
      - GET /api/items/funds_report/             Same as funds full report (alias)

    Attributes:
        queryset (QuerySet): Base queryset for the viewset.
        serializer_class (Serializer): Serializer used for representation.
    """
    queryset = MuseumItem.objects.all()
    serializer_class = MuseumItemSerializer

    @action(detail=True, methods=['get'])
    def related_by_exhibitions(self, request, pk=None):
        """
        Return other items that participated in the same exhibitions as the given item.

        Args:
            pk (int): Primary key of the source item.

        Returns:
            rest_framework.response.Response: list of MuseumItem serialized objects (excluding the source item).

        Example:
            GET /api/items/10/related_by_exhibitions/

            Response:
            [
              {"id": 12, "inventory_number": "B-12", "name": "Предмет 12", ...},
              {"id": 34, "inventory_number": "C-34", "name": "Предмет 34", ...}
            ]
        """
        qs = services.get_related_items_by_exhibitions(pk)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def written_off_count_by_fund(self, request):
        """
        Return counts of written-off items grouped by fund for a given date range.

        Query params:
            - from (YYYY-MM-DD) : optional start date (inclusive)
            - to   (YYYY-MM-DD) : optional end date (inclusive)

        Returns:
            rest_framework.response.Response: list of objects:
                - item__fund__id (int)
                - item__fund__name (str)
                - written_off_count (int)

        Example:
            GET /api/items/written_off_count_by_fund/?from=2023-01-01&to=2023-12-31

            Response:
            [
              {"item__fund__id": 1, "item__fund__name": "Живопись", "written_off_count": 2},
              {"item__fund__id": 3, "item__fund__name": "Археология", "written_off_count": 1}
            ]
        """
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        data = services.get_written_off_count_by_fund(from_date=from_date, to_date=to_date)
        return Response(data)

    @action(detail=False, methods=['get'])
    def fund_volume_percentage(self, request):
        """
        Return the percentage share of each fund by number of items.

        Returns:
            rest_framework.response.Response: list of objects:
                - id (int)
                - name (str)
                - count (int)
                - percentage (float)

        Example:
            GET /api/items/fund_volume_percentage/

            Response:
            [
              {"id": 1, "name": "Живопись", "count": 40, "percentage": 33.33},
              {"id": 2, "name": "Графика", "count": 30, "percentage": 25.0}
            ]
        """
        data = services.get_fund_volume_percentage()
        return Response(data)

    @action(detail=False, methods=['get'])
    def funds_report(self, request):
        """
        Alias for the full funds report (same structure as GET /api/funds/full_report/).

        Returns:
            rest_framework.response.Response: same structure as StorageFundViewSet.full_report.

        Example:
            GET /api/items/funds_report/

            Response:
            {
              "total_items": 120,
              "funds": [ ... ]
            }
        """
        data = services.get_full_funds_report()
        return Response(data)


class AuxiliaryCardIndexViewSet(viewsets.ModelViewSet):
    """
    CRUD for auxiliary card indexes that group thematic collections.
    """

    queryset = AuxiliaryCardIndex.objects.select_related('fund').all()
    serializer_class = AuxiliaryCardIndexSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    """
    CRUD for authors (first author of a museum item).
    """

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    CRUD for partner organizations that host exhibitions or receive items.
    """

    queryset = Organization.objects.select_related('address').all()
    serializer_class = OrganizationSerializer


class ExhibitionViewSet(viewsets.ModelViewSet):
    """
    CRUD for exhibitions.
    """

    queryset = Exhibition.objects.select_related('location_address', 'organization').all()
    serializer_class = ExhibitionSerializer


class ExhibitionParticipationViewSet(viewsets.ModelViewSet):
    """
    Manage participation of items in exhibitions.
    """

    queryset = ExhibitionParticipation.objects.select_related('item', 'exhibition').all()
    serializer_class = ExhibitionParticipationSerializer


class CollectionItemViewSet(viewsets.ModelViewSet):
    """
    Manage explicit links between collections and museum items.
    """

    queryset = CollectionItem.objects.select_related('collection', 'item').all()
    serializer_class = CollectionItemSerializer


class MovementActViewSet(viewsets.ModelViewSet):
    """
    CRUD for movement acts. performed_by is autofilled with the current user.
    """

    queryset = MovementAct.objects.prefetch_related('movements').all()
    serializer_class = MovementActSerializer

    def perform_create(self, serializer):
        performer = self.request.user if self.request.user.is_authenticated else None
        serializer.save(performed_by=performer)


class MovementViewSet(viewsets.ModelViewSet):
    """
    CRUD for movements (individual lines linked to an act).
    """

    queryset = Movement.objects.select_related(
        'act',
        'item',
        'collection',
        'external_organization',
        'exhibition',
        'from_fund',
        'to_fund',
    ).all()
    serializer_class = MovementSerializer
