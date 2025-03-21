from django.db import models

class InfoProduct(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    tig_id = models.IntegerField(default='-1')
    name = models.CharField(max_length=100, blank=True, default='')
    category = models.IntegerField(default='-1')
    price = models.FloatField(default='0')
    unit = models.CharField(max_length=20, blank=True, default='')
    availability = models.BooleanField(default=True)
    sale = models.BooleanField(default=False)
    discount = models.FloatField(default='0')
    comments = models.CharField(max_length=100, blank=True, default='')
    owner = models.CharField(max_length=20, blank=True, default='tig_orig')
    quantityInStock = models.IntegerField(default='0')
    sellprice = models.FloatField(default='0')

    class Meta:
        ordering = ('name',)

class Transactions(models.Model):
    date_transaction = models.DateTimeField()
    productId = models.IntegerField(default='-1')
    productName = models.CharField(max_length=100, blank=True, default='')
    type_transaction = models.CharField(max_length=100, blank=True, default='')
    quantity = models.IntegerField(default='0')
    price = models.FloatField(default='0')
    total = models.FloatField(default='0')

    class Meta:
        ordering = ('-date_transaction',)
