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
        all_tag_slugs = {tag['slug'] for tag in Tag.objects.all().values('slug')}
        upcnumber = pk
        if upcnumber in all_tag_slugs:
            self.create_log_item(upcnumber)
            return HttpResponse('shift')
        self.product = self.get_or_create_product(upcnumber)
        self.stock = self.create_stock_item()
        self.process_tags()
        return HttpResponse('ok')

    def process_tags(self):
        tag = self.pop_stack()
        while tag:
            self.product.tags.add(tag.name)
            self.stock.tags.add(tag.name)
            tag = self.pop_stack()

    def create_stock_item(self):
        stock = Stock(product=self.product)
        stock.save()
        return stock

    def create_log_item(self, upcnumber):
        # we have a character code
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
