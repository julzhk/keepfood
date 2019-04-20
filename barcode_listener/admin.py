# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Product, Stock, Log


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title', 'description']
    list_display = (
        'title',
        'id',
        'description',
        'upcnumber',
        'tag_list',
        'data_source'

    )
    list_filter = ('data_source', 'created_at', 'modified_at')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super(ProductAdmin, self).get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product',
        'date_use_by',
        'quantity_remaining',
        'tag_list',
        'created_at',
    )
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super(StockAdmin, self).get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'upcnumber', 'created_at')
    date_hierarchy = 'created_at'
