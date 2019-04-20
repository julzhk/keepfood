from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from flags.state import flag_enabled
from taggit.managers import TaggableManager
from taggit.models import Tag
from taggit.models import TaggedItemBase

from barcode_listener.barcode_lookup import Open_Food_Facts, UPC_Database, EAN_Data, EAN_Search, Mock_API
from barcode_listener.barcode_lookup import ProductNotFoundException


class CommonTags(object):
    """ These tags apply to both stock and products """
    content_object = None

    def set_use_by_date(self, days_in_future):
        """ any stock items given the tag 'six_months_life' have the expiry date bumped accordingly"""
        date_expiry = timezone.now() + timedelta(days=days_in_future)
        self.content_object.date_use_by = date_expiry
        self.content_object.save()
        return date_expiry

    def six_months_life(self):
        """ any stock items given the tag 'six_months_life' have the expiry date bumped accordingly"""
        return self.set_use_by_date(days_in_future=30 * 6)

    def two_weeks_life(self):
        """ any stock items given this tag have the expiry date bumped accordingly"""
        return self.set_use_by_date(days_in_future=7 * 2)

    def one_weeks_life(self):
        """ any stock items given this tag have the expiry date bumped accordingly"""
        return self.set_use_by_date(days_in_future=7)

    def frozen(self):
        """ any stock items given the tag 'six_months_life' have the expiry date bumped accordingly"""
        date_expiry = timezone.now() + timedelta(days=30 * 6)
        self.content_object.date_use_by = date_expiry
        self.content_object.save()
        return date_expiry

class TaggedProduct(TaggedItemBase, CommonTags):
    content_object = models.ForeignKey('Product', on_delete=models.CASCADE)

class TaggedStock(TaggedItemBase, CommonTags):
    content_object = models.ForeignKey('Stock', on_delete=models.CASCADE)

    def set_remaining_quantity(self, qty_percent):
        """ set stock items % remaining"""
        self.content_object.quantity_remaining = qty_percent
        self.content_object.save()
        return qty_percent

    def remaining_100(self):
        return self.set_remaining_quantity(qty_percent=100)

    def remaining_75(self):
        return self.set_remaining_quantity(qty_percent=75)

    def remaining_50(self):
        return self.set_remaining_quantity(qty_percent=50)

    def remaining_25(self):
        return self.set_remaining_quantity(qty_percent=25)

    def remaining_10(self):
        return self.set_remaining_quantity(qty_percent=10)

    def remaining_0(self):
        return self.set_remaining_quantity(qty_percent=0)

    def is_can(self):
        print('is a can')

    def delete_stock(self):
        # delete all stock items with supplied UPC
        product = self.content_object.product
        Stock.objects.filter(product=product).delete()

class Product(models.Model):
    title = models.CharField(max_length=128, blank=True)
    description = models.CharField(max_length=128, blank=True)
    upcnumber = models.CharField(max_length=128, blank=True)
    data_source = models.CharField(
        default=settings.PLACEHOLDER_LABEL,
        max_length=128,
        blank=True)

    created_at = models.DateTimeField(blank=True)
    modified_at = models.DateTimeField(blank=True)

    tags = TaggableManager(through=TaggedProduct, blank=True)

    class Meta:
        ordering = ['-modified_at', '-created_at']

    def __str__(self):
        return f'{self.upcnumber}: {self.title}{self.description}'

    def save(self, *args, **kwargs):
        """ auto date stamp """
        self.modified_at = timezone.now()
        if not self.id:
            self.created_at = timezone.now()
        return super(Product, self).save(*args, **kwargs)

    @classmethod
    def get_or_create_product(cls, upcnumber):
        """
        :param upcnumber: str
        :return: Product: object
        """
        if Product.objects.filter(upcnumber=upcnumber).exists():
            print('found')
            return Product.objects.get(upcnumber=upcnumber)
        else:
            print('not found')
            return Product().populate(upc=upcnumber)

    @classmethod
    def populate(cls, upc):
        product_data = None
        if flag_enabled('USE_LIMITED_API_CALLS'):
            API_klass_list = [Open_Food_Facts, ]

        else:
            API_klass_list = [Open_Food_Facts,
                              UPC_Database,
                              EAN_Data,
                              EAN_Search
                              ]
        if settings.MOCK_API_CALLS:
            API_klass_list = [Mock_API, ]

        for klass in API_klass_list:
            try:
                product_data = klass(upc=upc).execute()
                break
            except ProductNotFoundException:
                print('not found')
            except Exception as err:
                print(err)
                # continue anyway
        if product_data is None:
            print('not found anywhere - create placeholder')
            product_data = cls.create_placeholder_product(upc)
        p = Product(**product_data)
        p.save()
        return p

    @classmethod
    def create_placeholder_product(cls, upc):
        product_data = {
            'title': 'Not found',
            'description': 'Not found',
            'upcnumber': upc
        }
        return product_data

class Stock(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    date_use_by = models.DateTimeField(blank=True)
    date_started = models.DateTimeField(blank=True)
    quantity_remaining = models.IntegerField(default=100)
    created_at = models.DateTimeField(blank=True)
    modified_at = models.DateTimeField(blank=True)

    tags = TaggableManager(through=TaggedStock, blank=True)

    class Meta:
        ordering = ['-modified_at', '-created_at']
        verbose_name_plural = 'Stock'

    def __str__(self):
        return f'{self.product.upcnumber}: {self.product.title}{self.product.description} {self.quantity_remaining}%'

    def save(self, *args, **kwargs):
        """ auto date stamp """
        self.modified_at = timezone.now()
        if not self.id:
            self.created_at = timezone.now()
            self.quantity_remaining = 100
            self.date_use_by = timezone.now() + timedelta(days=settings.DEFAULT_DAYS_USE_BY)
        return super(Stock, self).save(*args, **kwargs)


class Log(models.Model):
    upcnumber = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(blank=True)

    def save(self, *args, **kwargs):
        """ auto date stamp """
        if not self.id:
            self.created_at = timezone.now()
        return super(Log, self).save(*args, **kwargs)

    class Meta:
        ordering = ['pk', ]
        verbose_name_plural = 'Log'

