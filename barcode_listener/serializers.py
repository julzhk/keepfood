from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'age', 'alias', 'brand', 'category',
                  'color', 'description', 'error', 'gender',
                  'msrp', 'newupc', 'rate_down', 'rate_up', 'size',
                  'st0s', 'title', 'type', 'unit', 'upcnumber',
                  )
