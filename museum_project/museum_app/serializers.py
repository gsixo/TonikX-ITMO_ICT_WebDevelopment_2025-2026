from rest_framework import serializers
from .models import (
    Address, StorageFund, AuxiliaryCardIndex, Collection, Author,
    MuseumItem, Organization, Exhibition, ExhibitionParticipation,
    CollectionItem, MovementAct, Movement
)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class StorageFundSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source='address',
        write_only=True,
        required=False
    )

    class Meta:
        model = StorageFund
        fields = ['id', 'name', 'fund_type', 'description', 'address', 'address_id']


class AuxiliaryCardIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuxiliaryCardIndex
        fields = '__all__'


class CollectionSerializer(serializers.ModelSerializer):
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    auxiliary_index = AuxiliaryCardIndexSerializer(read_only=True)
    auxiliary_index_id = serializers.PrimaryKeyRelatedField(
        queryset=AuxiliaryCardIndex.objects.all(),
        source='auxiliary_index',
        write_only=True,
        required=False
    )

    class Meta:
        model = Collection
        fields = ['id','name','auxiliary_index','auxiliary_index_id','items_count']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class MuseumItemSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), source='author', write_only=True, required=False)
    fund = StorageFundSerializer(read_only=True)
    fund_id = serializers.PrimaryKeyRelatedField(queryset=StorageFund.objects.all(), source='fund', write_only=True)
    collection = CollectionSerializer(read_only=True)
    collection_id = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(),
        source='collection',
        write_only=True,
        required=False
    )

    class Meta:
        model = MuseumItem
        fields = [
            'id','inventory_number','name','creation_date','creation_exact',
            'author','author_id','fund','fund_id','collection','collection_id',
            'notes','is_written_off'
        ]


class OrganizationSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source='address',
        write_only=True,
        required=False
    )

    class Meta:
        model = Organization
        fields = ['id', 'name', 'phone', 'contact_person', 'address', 'address_id']


class ExhibitionSerializer(serializers.ModelSerializer):
    location_address = AddressSerializer(read_only=True)
    location_address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source='location_address',
        write_only=True,
        required=False
    )
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source='organization',
        write_only=True,
        required=False
    )

    class Meta:
        model = Exhibition
        fields = [
            'id', 'name', 'start_date', 'end_date', 'notes',
            'location_address', 'location_address_id',
            'organization', 'organization_id'
        ]


class ExhibitionParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExhibitionParticipation
        fields = '__all__'


class CollectionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionItem
        fields = '__all__'


class MovementSerializer(serializers.ModelSerializer):
    item = MuseumItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=MuseumItem.objects.all(),
        source='item',
        write_only=True,
        required=False,
        allow_null=True,
    )
    collection = CollectionSerializer(read_only=True)
    collection_id = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(),
        source='collection',
        write_only=True,
        required=False,
        allow_null=True,
    )
    external_organization = OrganizationSerializer(read_only=True)
    external_organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source='external_organization',
        write_only=True,
        required=False,
        allow_null=True,
    )
    exhibition = ExhibitionSerializer(read_only=True)
    exhibition_id = serializers.PrimaryKeyRelatedField(
        queryset=Exhibition.objects.all(),
        source='exhibition',
        write_only=True,
        required=False,
        allow_null=True,
    )
    from_fund = StorageFundSerializer(read_only=True)
    from_fund_id = serializers.PrimaryKeyRelatedField(
        queryset=StorageFund.objects.all(),
        source='from_fund',
        write_only=True,
        required=False,
        allow_null=True,
    )
    to_fund = StorageFundSerializer(read_only=True)
    to_fund_id = serializers.PrimaryKeyRelatedField(
        queryset=StorageFund.objects.all(),
        source='to_fund',
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Movement
        fields = '__all__'


class MovementActSerializer(serializers.ModelSerializer):
    movements = MovementSerializer(read_only=True, many=True)

    class Meta:
        model = MovementAct
        fields = '__all__'