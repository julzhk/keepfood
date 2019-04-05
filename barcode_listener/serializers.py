import os
import pprint

import requests
from rest_framework import serializers

UPC_KEY = os.environ.get('UPC_KEY', '??')  # https://upcdatabase.org/

UPCDATABASE_URL_PATTERN = "https://api.upcdatabase.org/product/%s/%s"
UPC_LOOKUP_ERROR = 'upc number error'

from .models import Product


def UPC_lookup(upc):
    ''' uses UPC's V3 API '''
    url = UPCDATABASE_URL_PATTERN % (upc, UPC_KEY)
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


def clean_up_keys(data):
    try:
        del data['status']
    except KeyError:
        pass
    return {k.replace('/', '_'): data[k] for k in data}


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ('upcnumber',)

    def create(self, validated_data):
        upcnumber = validated_data.get('upcnumber')
        data = UPC_lookup(upcnumber)
        validated_data = clean_up_keys(data)
        return super(ProductSerializer, self).create(validated_data)
