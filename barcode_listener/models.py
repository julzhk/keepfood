from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager


class Product(models.Model):
    age = models.CharField(max_length=128, blank=True)
    alias = models.CharField(max_length=128, blank=True)
    brand = models.CharField(max_length=128, blank=True)
    category = models.CharField(max_length=128, blank=True)
    color = models.CharField(max_length=128, blank=True)
    description = models.CharField(max_length=128, blank=True)
    error = models.BooleanField(default=False)
    gender = models.CharField(max_length=128, blank=True)
    msrp = models.CharField(max_length=12, blank=True)
    newupc = models.CharField(max_length=128, blank=True)
    rate_down = models.CharField(max_length=128, blank=True)
    rate_up = models.CharField(max_length=12, blank=True)
    size = models.CharField(max_length=128, blank=True)
    st0s = models.CharField(max_length=128, blank=True)
    title = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=128, blank=True)
    unit = models.CharField(max_length=128, blank=True)
    upcnumber = models.CharField(max_length=128, blank=True)

    created_at = models.DateTimeField(blank=True)
    modified_at = models.DateTimeField(blank=True)

    tags = TaggableManager()

    class Meta:
        ordering = ['-modified_at', '-created_at']

    def save(self, *args, **kwargs):
        """ auto date stamp """
        self.modified_at = timezone.now()
        if not self.id:
            self.created_at = timezone.now()
        return super(Product, self).save(*args, **kwargs)


class Stock(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    date_use_by = models.DateTimeField(blank=True)
    quantity_remaining = models.IntegerField(default=100)
    created_at = models.DateTimeField(blank=True)
    modified_at = models.DateTimeField(blank=True)

    tags = TaggableManager()

    class Meta:
        ordering = ['-modified_at', '-created_at']
        verbose_name_plural = 'Stock'

    def save(self, *args, **kwargs):
        """ auto date stamp """
        self.modified_at = timezone.now()
        if not self.id:
            self.created_at = timezone.now()
            self.quantity_remaining = 100
            self.date_use_by = timezone.now() + timedelta(days=settings.DEFAULT_DAYS_USE_BY)
        return super(Stock, self).save(*args, **kwargs)


class Log(models.Model):
    upcnumber = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(blank=True)

    def save(self, *args, **kwargs):
        """ auto date stamp """
        if not self.id:
            self.created_at = timezone.now()
        return super(Log, self).save(*args, **kwargs)

    class Meta:
        ordering = ['pk', ]
        verbose_name_plural = 'Log'
