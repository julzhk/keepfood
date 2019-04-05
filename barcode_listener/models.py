from django.db import models
from django.utils import timezone

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

    class Meta:
        ordering = ['-modified_at', '-created_at']

    def save(self, *args, **kwargs):
        """ auto date stamp """
        self.modified_at = timezone.now()
        if not self.id:
            self.created_at = timezone.now()
        return super(Product, self).save(*args, **kwargs)
