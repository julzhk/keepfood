import os
import pprint

import requests
from django.shortcuts import HttpResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

UPC_KEY = os.environ.get('UPC_KEY', '??')  # https://upcdatabase.org/
KEEPFOOD_KEY = os.environ.get('KEEPFOOD_KEY', '??')
KEEPFOOD_URL = os.environ.get('KEEPFOOD_URL', '??')
UPC_LOOKUP_ERROR = 'upc number error'
UPCDATABASE_URL_PATTERN = "https://api.upcdatabase.org/product/%s/%s"

from .models import Product
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


def listener(request):
    return HttpResponse('boom')