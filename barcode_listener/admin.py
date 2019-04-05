# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Product, Stock


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'brand',
        'category',
        'description',
        'newupc',
        'title',
        'type',
        'upcnumber',
    )
    list_filter = ('error', 'created_at', 'modified_at')
    date_hierarchy = 'created_at'


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product',
        'date_use_by',
        'quantity_remaining',
        'created_at',
    )
    date_hierarchy = 'created_at'
