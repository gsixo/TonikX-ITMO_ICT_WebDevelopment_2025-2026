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
    class Meta:
        model = StorageFund
        fields = '__all__'


class AuxiliaryCardIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuxiliaryCardIndex
        fields = '__all__'


class CollectionSerializer(serializers.ModelSerializer):
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    class Meta:
        model = Collection
        fields = ['id','name','auxiliary_index','items_count']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class MuseumItemSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), source='author', write_only=True, required=False)
    fund = StorageFundSerializer(read_only=True)
    fund_id = serializers.PrimaryKeyRelatedField(queryset=StorageFund.objects.all(), source='fund', write_only=True)

    class Meta:
        model = MuseumItem
        fields = ['id','inventory_number','name','creation_date','creation_exact','author','author_id','fund','fund_id','collection','notes','is_written_off']


class ExhibitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exhibition
        fields = '__all__'


class ExhibitionParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExhibitionParticipation
        fields = '__all__'


class CollectionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionItem
        fields = '__all__'


class MovementActSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovementAct
        fields = '__all__'


class MovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movement
        fields = '__all__'