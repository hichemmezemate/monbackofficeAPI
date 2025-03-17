from django.contrib import admin

from .models import InfoProduct, Transactions

admin.site.register(Transactions)
admin.site.register(InfoProduct)
