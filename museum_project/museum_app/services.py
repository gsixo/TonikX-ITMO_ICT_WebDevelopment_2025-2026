from django.db.models import Count, OuterRef, Subquery, DateField
from django.db.models.functions import Coalesce
from .models import StorageFund, Collection, MuseumItem, ExhibitionParticipation, Movement, MovementType, MovementAct

def get_funds_exhibitions_count():
    """
    Для каждого фонда — количество уникальных выставок, в которых участвовали предметы фонда.
    """
    qs = StorageFund.objects.annotate(
        exhibitions_count=Count('items__exhibitions__exhibition', distinct=True)
    ).values('id', 'name', 'exhibitions_count')
    return list(qs)

def get_collections_items_count():
    """
    Для каждого комплекта — количество единиц в комплекте.
    """
    qs = Collection.objects.annotate(
        items_count=Count('collection_items', distinct=True)
    ).values('id', 'name', 'items_count')
    return list(qs)

def get_related_items_by_exhibitions(item_id):
    """
    Для заданного предмета вернуть другие предметы,
    которые участвовали в тех же выставках.
    """
    ex_ids = ExhibitionParticipation.objects.filter(item_id=item_id).values_list('exhibition_id', flat=True)
    qs = MuseumItem.objects.filter(exhibitions__exhibition_id__in=ex_ids).exclude(id=item_id).distinct()
    return qs

def get_written_off_count_by_fund(from_date=None, to_date=None):
    """
    Количество списанных предметов по каждому фонду в период.
    Учитываем списания по предметам и по коллекциям.
    """
    qs = Movement.objects.filter(movement_type=MovementType.WRITE_OFF)
    if from_date:
        qs = qs.filter(date__gte=from_date)
    if to_date:
        qs = qs.filter(date__lte=to_date)

    direct_ids = set(qs.filter(item__isnull=False).values_list('item_id', flat=True))

    coll_ids = list(qs.filter(collection__isnull=False).values_list('collection_id', flat=True))
    if coll_ids:
        items_from_collections = MuseumItem.objects.filter(collection__in=coll_ids).values_list('id', flat=True)
        direct_ids.update(list(items_from_collections))

    if not direct_ids:
        return []

    result = MuseumItem.objects.filter(id__in=direct_ids).values('fund__id', 'fund__name').annotate(
        written_off_count=Count('id')
    )
    return list(result)

def get_fund_volume_percentage():
    """
    Процентное соотношение объёма фондов (по количеству предметов).
    """
    total = MuseumItem.objects.count()
    funds = StorageFund.objects.annotate(count=Count('items')).values('id', 'name', 'count')
    res = []
    for f in funds:
        pct = (f['count'] / total * 100) if total else 0
        res.append({'id': f['id'], 'name': f['name'], 'count': f['count'], 'percentage': round(pct, 2)})
    return res

def get_full_funds_report():
    """
    Для каждого фонда:
      - список предметов
      - для каждого предмета: инв.номер, название, первая дата поступления (movement_type=RECEIVE),
        количество выставок, флаг списанности.
      - количества предметов в фонде
    Возвращает dict: {'total_items': int, 'funds': [{...}, ...]}
    """
    first_receive_qs = Movement.objects.filter(
        item=OuterRef('pk'),
        movement_type=MovementType.RECEIVE
    ).order_by('date').values('date')[:1]

    items_qs = MuseumItem.objects.annotate(
        first_receive_date=Subquery(first_receive_qs, output_field=DateField()),
        exhibitions_count=Count('exhibitions__exhibition', distinct=True)
    )

    total_items = MuseumItem.objects.count()
    report = []

    funds = StorageFund.objects.all().order_by('name')
    for fund in funds:
        fund_items_qs = items_qs.filter(fund=fund).order_by('inventory_number')
        items_list = []
        for item in fund_items_qs:
            items_list.append({
                'id': item.id,
                'inventory_number': item.inventory_number,
                'name': item.name,
                'first_receive_date': item.first_receive_date,
                'exhibitions_count': item.exhibitions_count,
                'is_written_off': item.is_written_off,
            })
        report.append({
            'fund_id': fund.id,
            'fund_name': fund.name,
            'items_count': fund_items_qs.count(),
            'items': items_list,
        })

    return {'total_items': total_items, 'funds': report}