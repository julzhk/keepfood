import os

from rest_framework import serializers

UPC_KEY = os.environ.get('UPC_KEY', '??')  # https://upcdatabase.org/

UPCDATABASE_URL_PATTERN = "https://api.upcdatabase.org/product/%s/%s"
UPC_LOOKUP_ERROR = 'upc number error'

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('upcnumber',)
