import os
import pprint

import requests
from django.shortcuts import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from taggit.models import Tag

UPC_KEY = os.environ.get('UPC_KEY', '??')  # https://upcdatabase.org/
KEEPFOOD_KEY = os.environ.get('KEEPFOOD_KEY', '??')
KEEPFOOD_URL = os.environ.get('KEEPFOOD_URL', '??')
UPC_LOOKUP_ERROR = 'upc number error'
UPCDATABASE_URL_PATTERN = "https://api.upcdatabase.org/product/%s/%s"
RESET_STACK_TAG_NAME = 'reset_stack'
DELETE_TAG_NAME = 'delete_stock'


class ControlCodeException(Exception):
    pass

from .models import Product, Stock, Log
from .serializers import ProductSerializer


def UPC_lookup(upc):
    ''' uses UPC's V3 API '''
    url = UPCDATABASE_URL_PATTERN % (upc, (UPC_KEY))
    response = requests.request("GET", url, headers={'cache-control': "no-cache", })
    product_data = response.json()
    print("-" * 8)
    pprint.pprint(product_data)
    print("-" * 8)
    if product_data.get('error'):
        product_data = {
            'upcnumber': upc,
            'error': True
        }
    return product_data


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows product to be viewed or edited.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=True, methods=['post'])
    def scan(self, request, pk=None):
        upcnumber = pk
        try:
            self.process_control_characters(upcnumber=upcnumber)
        except ControlCodeException:
            return HttpResponse('control')
        self.product = self.get_or_create_product(upcnumber)
        self.stock = self.create_stock_item()
        self.process_tags()
        return HttpResponse('ok')

    def process_control_characters(self, upcnumber):
        """ if upc code is a control character, add to the stack and return with no further processing"""
        self.process_reset_stack_command(upcnumber)
        all_tag_slugs = {tag['slug'] for tag in Tag.objects.all().values('slug')}
        if upcnumber in all_tag_slugs:
            self.create_log_item(upcnumber)
            raise ControlCodeException()

    def process_reset_stack_command(self, upcnumber):
        reset_stack_tag = Tag.objects.filter(name=RESET_STACK_TAG_NAME).first()
        if reset_stack_tag and upcnumber == reset_stack_tag.slug:
            Log.objects.all().delete()
            raise ControlCodeException()


    def process_tags(self):
        tag = self.pop_stack()
        while tag:
            tag_name = tag.name
            self.product.tags.add(tag_name)
            self.stock.tags.add(tag_name)
            for stock_tag in self.stock.taggedstock_set.all():
                self.execute_tag_methods(stock_tag, tag_name)
            tag = self.pop_stack()

    def execute_tag_methods(self, stock_tag, tag_name):
        try:
            func = getattr(stock_tag, tag_name)
            r = func()
            print(f'{func.__name__} : {r}')
        except AttributeError:
            print(f'no {tag_name} method')

    def create_stock_item(self):
        stock = Stock(product=self.product)
        stock.save()
        return stock

    def create_log_item(self, upcnumber):
        # we have a character code, add to the stack
        Log(upcnumber=upcnumber).save()

    def get_or_create_product(self, upcnumber):
        if Product.objects.filter(upcnumber=upcnumber).exists():
            product = Product.objects.get(upcnumber=upcnumber)
        else:
            data = UPC_lookup(upcnumber)
            validated_data = clean_up_keys(data)
            product = Product(**validated_data)
            product.save()
        return product


    def pop_stack(self):
        """ if there's anything on the stack get it, and delete it from the Log"""
        if Log.objects.count():
            log = Log.objects.last()
            tag = Tag.objects.get(slug=log.upcnumber)
            log.delete()
            return tag


def listener(request):
    """ home page """
    return HttpResponse('boom')


def clean_up_keys(data):
    """
    * some returned data keys have / in them..
    * we don't need 'status' either"""
    try:
        del data['status']
    except KeyError:
        pass
    return {k.replace('/', '_'): data[k] for k in data}
