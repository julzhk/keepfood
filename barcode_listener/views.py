from django.conf import settings
from django.shortcuts import HttpResponse, Http404
from django.template.response import TemplateResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from taggit.models import Tag

from .models import Product, Stock, Log
from .serializers import ProductSerializer

RESET_STACK_TAG_NAME = 'reset_stack'
DELETE_TAG_NAME = 'delete_stock'


class ControlCodeException(Exception):
    pass


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
        except ControlCodeException as err:
            return HttpResponse('control' + str(err),
                                content_type="text/plain")
        self.product = Product().get_or_create_product(upcnumber)
        self.stock = self.create_stock_item()
        self.process_tags()
        if self.product.data_source == settings.PLACEHOLDER_LABEL:
            return Http404('not found')
        return HttpResponse('ok', content_type="text/plain")

    def process_control_characters(self, upcnumber):
        """ if upc code is a control character, add to the stack and return with no further processing"""
        self.process_reset_stack_command(upcnumber)
        try:
            tag = Tag.objects.get(slug=upcnumber)
            self.create_log_item(upcnumber)
            raise ControlCodeException(tag.name)
        except Tag.DoesNotExist:
            pass

    def process_reset_stack_command(self, upcnumber):
        reset_stack_tag = Tag.objects.filter(name=RESET_STACK_TAG_NAME).first()
        if reset_stack_tag and upcnumber == reset_stack_tag.slug:
            Log.objects.all().delete()
            raise ControlCodeException()

    def process_tags(self):
        """ Tags are pulled off the stack and associated code executed on this new STOCK object """
        tag = self.pop_stack()
        while tag:
            tag_name = tag.name
            # product tags not supported: self.product.tags.add(tag_name)
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


    def pop_stack(self):
        """ if there's anything on the stack get it, and delete it from the Log"""
        if Log.objects.count():
            log = Log.objects.last()
            tag = Tag.objects.get(slug=log.upcnumber)
            log.delete()
            return tag


def listener(request):
    """ home page : shows tag control codes"""

    return TemplateResponse(request, 'barcode_listener/control_codes.html', {'tags': Tag.objects.all()})
