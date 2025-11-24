from django.db import models

from django.db import models
from django.conf import settings


class Address(models.Model):
    line = models.CharField('Адрес', max_length=300)

    def __str__(self):
        return self.line


class FundType(models.TextChoices):
    PAINTING = 'painting', 'Живопись'
    GRAPHICS = 'graphics', 'Графика'
    ICON = 'icon', 'Икона'
    SCULPTURE = 'sculpture', 'Скульптура'
    DPA = 'dpa', 'ДПИ'
    NUMISMATICS = 'numismatics', 'Нумизматика'
    ARCHAEOLOGY = 'archaeology', 'Археология'
    MANUSCRIPTS = 'manuscripts', 'Рукописи'
    RARE_BOOK = 'rare_book', 'Редкая книга'
    OTHER = 'other', 'Другое'

class StorageFund(models.Model):
    name = models.CharField('Название фонда', max_length=200)
    fund_type = models.CharField('Тип фонда', max_length=30, choices=FundType.choices, default=FundType.OTHER)
    address = models.ForeignKey(Address, verbose_name='Адрес фонда', null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Фонд'
        verbose_name_plural = 'Фонды'

    def __str__(self):
        return f"{self.name} ({self.get_fund_type_display()})"


class AuxiliaryCardIndex(models.Model):
    name = models.CharField('Название картотеки', max_length=200)
    fund = models.ForeignKey(StorageFund, related_name='aux_indices', on_delete=models.CASCADE)
    notes = models.TextField('Заметки', blank=True)

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField('Название комплекта', max_length=200)
    auxiliary_index = models.ForeignKey(AuxiliaryCardIndex, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Комплект'
        verbose_name_plural = 'Комплекты'

    def __str__(self):
        return self.name


class Author(models.Model):
    full_name = models.CharField('ФИО', max_length=200)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    country = models.CharField('Страна', max_length=100, blank=True)

    def __str__(self):
        return self.full_name


class MuseumItem(models.Model):
    inventory_number = models.CharField('Инв. номер', max_length=100, unique=True)
    name = models.CharField('Название', max_length=300)
    creation_date = models.DateField('Дата создания', null=True, blank=True)
    creation_exact = models.BooleanField('Точная дата', default=True, help_text='True — точная, False — приблизительная')
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.SET_NULL)
    fund = models.ForeignKey(StorageFund, related_name='items', on_delete=models.PROTECT)
    collection = models.ForeignKey(Collection, null=True, blank=True, related_name='items', on_delete=models.SET_NULL)
    notes = models.TextField('Заметки', blank=True)
    is_written_off = models.BooleanField('Списан', default=False)

    class Meta:
        verbose_name = 'Музейный предмет'
        verbose_name_plural = 'Музейные предметы'

    def __str__(self):
        return f"{self.inventory_number} — {self.name}"


class Organization(models.Model):
    name = models.CharField('Название организации', max_length=300)
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL)
    phone = models.CharField('Телефон', max_length=50, blank=True)
    contact_person = models.CharField('Контактное лицо', max_length=200, blank=True)

    def __str__(self):
        return self.name


class Exhibition(models.Model):
    name = models.CharField('Название выставки', max_length=300)
    location_address = models.ForeignKey(Address, null=True, blank=True, related_name='exhibitions', on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization, null=True, blank=True, related_name='exhibitions', on_delete=models.SET_NULL)
    start_date = models.DateField('Дата начала')
    end_date = models.DateField('Дата окончания')
    notes = models.TextField('Заметки', blank=True)

    class Meta:
        verbose_name = 'Выставка'
        verbose_name_plural = 'Выставки'

    def __str__(self):
        return f"{self.name} ({self.start_date} — {self.end_date})"


class ExhibitionParticipation(models.Model):
    item = models.ForeignKey(MuseumItem, related_name='exhibitions', on_delete=models.CASCADE)
    exhibition = models.ForeignKey(Exhibition, related_name='items', on_delete=models.CASCADE)
    included_as_part_of_collection = models.BooleanField('Как часть комплекта', default=False)

    class Meta:
        unique_together = ('item', 'exhibition')

    def __str__(self):
        return f"{self.item} -> {self.exhibition}"


class CollectionItem(models.Model):
    collection = models.ForeignKey(Collection, related_name='collection_items', on_delete=models.CASCADE)
    item = models.ForeignKey(MuseumItem, related_name='collection_link', on_delete=models.CASCADE)
    position_note = models.CharField('Позиция в комплекте', max_length=200, blank=True)

    class Meta:
        unique_together = ('collection', 'item')

    def __str__(self):
        return f"{self.collection} : {self.item}"


class MovementType(models.TextChoices):
    RECEIVE = 'receive', 'Прием на хранение'
    TRANSFER_EXHIB = 'transfer_exhibition', 'Передача на выставку'
    RETURN_FROM_EXHIB = 'return', 'Возвращение с выставки'
    WRITE_OFF = 'write_off', 'Списание'
    INTERNAL_TRANSFER = 'internal_transfer', 'Внутренний перевод'


class MovementAct(models.Model):
    act_number = models.CharField('Номер акта', max_length=100, unique=True)
    created_at = models.DateTimeField('Дата создания акта', auto_now_add=True)
    movement_type = models.CharField('Тип акта', max_length=30, choices=MovementType.choices)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    museum_director_name = models.CharField('Руководитель музея', max_length=200, blank=True)
    fund_keeper_name = models.CharField('Хранитель фонда', max_length=200, blank=True)
    notes = models.TextField('Заметки', blank=True)

    def __str__(self):
        return f"Act {self.act_number} ({self.get_movement_type_display()})"


class Movement(models.Model):
    act = models.ForeignKey(MovementAct, related_name='movements', on_delete=models.CASCADE)
    item = models.ForeignKey(MuseumItem, related_name='movements', null=True, blank=True, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, related_name='movements', null=True, blank=True, on_delete=models.CASCADE)

    external_organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    exhibition = models.ForeignKey(Exhibition, null=True, blank=True, on_delete=models.SET_NULL)

    from_fund = models.ForeignKey(StorageFund, null=True, blank=True, related_name='movements_from', on_delete=models.SET_NULL)
    to_fund = models.ForeignKey(StorageFund, null=True, blank=True, related_name='movements_to', on_delete=models.SET_NULL)

    movement_type = models.CharField('Тип движения', max_length=30, choices=MovementType.choices)
    date = models.DateField('Дата движения')
    note = models.TextField('Заметки', blank=True)

    def __str__(self):
        target = self.item or self.collection
        return f"Movement {self.movement_type} — {target} on {self.date}"