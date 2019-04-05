from django.db import models
from django.utils import timezone

class Product(models.Model):
    age = models.CharField(max_length=128)
    alias = models.CharField(max_length=128)
    brand = models.CharField(max_length=128)
    category = models.CharField(max_length=128)
    color = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    error = models.BooleanField(default=False)
    gender = models.CharField(max_length=128)
    msrp = models.CharField(max_length=12)
    newupc = models.CharField(max_length=128)
    rate_down = models.CharField(max_length=128)
    rate_up = models.CharField(max_length=12)
    size = models.CharField(max_length=128)
    st0s = models.CharField(max_length=128)
    title = models.CharField(max_length=128)
    type = models.CharField(max_length=128)
    unit = models.CharField(max_length=128)
    upcnumber = models.CharField(max_length=128)

    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()

    class Meta:
        ordering = ['-modified_at', '-created_at']

    def save(self, *args, **kwargs):
        """ auto date stamp """
        self.modified_at = timezone.now()
        if not self.id:
            self.created_at = timezone.now()
        return super(Product, self).save(*args, **kwargs)
