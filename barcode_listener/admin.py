# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Product


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
