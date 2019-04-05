from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import ProductSerializer
from .models import Product

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows product to be viewed or edited.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


def listener(request):
    return HttpResponse('boom')