import base64
import hashlib
import hmac
import logging
import os
import pprint
from datetime import timedelta

import requests
from django.conf import settings
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from taggit.models import Tag
from taggit.models import TaggedItemBase

UPC_KEY = os.environ.get('UPC_KEY', '??')  # https://upcdatabase.org/
UPC_LOOKUP_ERROR = 'upc number error'
UPCDATABASE_URL_PATTERN = "https://api.upcdatabase.org/product/%s/%s"
EANDATA_URL_PATTERN = "https://eandata.com/feed/?v=3&keycode=%s&mode=json&find=%s"
DIGIT_EYES_KEY_M = os.environ.get('DIGIT_EYES_KEY_M', '??')
DIGIT_EYES_KEY_K = os.environ.get('DIGIT_EYES_KEY_K', '??')
EAN_KEY = os.environ.get('EAN_KEY', '??')


def generate_digiteyes_url(upc, sig, auth_key_k=DIGIT_EYES_KEY_K):
    DIGIT_EYES_URL = 'https://www.digit-eyes.com/gtin/v2_0/?upcCode={upc}&' \
                     'language=en&app_key={key}&signature={signature}'
    return DIGIT_EYES_URL.format(
        upc=upc,
        key=auth_key_k,
        signature=sig,
    )

def generate_signature(upc, auth_key_m=DIGIT_EYES_KEY_M):
    sha_hash = hmac.new(str.encode(auth_key_m), str.encode(upc), hashlib.sha1)
    sig = base64.b64encode(sha_hash.digest()).decode()
    return sig

def DigitEyes_lookup(upc, auth_key_m=DIGIT_EYES_KEY_M, auth_key_k=DIGIT_EYES_KEY_K):
    '''
        uses UPC's V3 API
    '''
    try:
        sig = generate_signature(upc, auth_key_m)
        url = generate_digiteyes_url(upc, sig, auth_key_k)
        logging.debug(url)
        response = requests.request("GET", url, headers={'cache-control': "no-cache", })
        product_data = response.json()
        print("-DIGIT EYES - " * 8)
        pprint.pprint(product_data)
        print("-" * 8)
        if product_data.get('return_message').lower() != 'success':
            return None
        return product_data
    except Exception as err:
        print(err)
        logging.error(err)
        return None

def UPC_lookup(upc):
    '''
        uses UPC's V3 API
    '''
    try:
        url = UPCDATABASE_URL_PATTERN % (upc, (UPC_KEY))
        response = requests.request("GET", url, headers={'cache-control': "no-cache", })
        product_data = response.json()
        print("-UPCDATABASE - " * 8)
        pprint.pprint(product_data)
        print("-" * 8)
        if product_data.get('error'):
            return None
        return product_data
    except Exception as err:
        print(err)
        logging.error(err)
        return None

def EAN_lookup(upc):
    try:
        url = EANDATA_URL_PATTERN % (EAN_KEY, upc)
        response = requests.request("GET", url, headers={'cache-control': "no-cache", })
        product_data = response.json()
        print("EAN LOOKUP " * 8)
        pprint.pprint(product_data)
        print("-" * 8)
        return product_data
        # title = product_data.get('product')[0].get('attributes', {}).get('product', '-')
        # product_data = {
        #     'title': title,
        #     'description': '',
        #     'upcnumber': upc
        # }
    except Exception as err:
        print(err)
        logging.error(err)
        return None

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

    def delete_stock(self):
        # delete all stock items with supplied UPC
        product = self.content_object.product
        Stock.objects.filter(product=product).delete()

class Product(models.Model):
    title = models.CharField(max_length=128, blank=True)
    description = models.CharField(max_length=128, blank=True)
    upcnumber = models.CharField(max_length=128, blank=True)

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
    def populate(cls, upc):
        product_data = DigitEyes_lookup(upc=upc)
        if product_data:
            product_data = {
                'title': product_data.get('description'),
                'description': product_data['description'],
                'upcnumber': product_data['upc_code'],
            }
        else:
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

