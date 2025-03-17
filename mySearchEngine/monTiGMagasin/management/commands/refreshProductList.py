from django.core.management.base import BaseCommand
from monTiGMagasin.models import InfoProduct
from monTiGMagasin.serializers import InfoProductSerializer
from monTiGMagasin.config import baseUrl
import requests
import time

class Command(BaseCommand):
    help = 'Refresh the list of products from TiG server.'

    def handle(self, *args, **options):
        self.stdout.write('['+time.ctime()+'] Refreshing data...')
        response = requests.get(baseUrl+'products/')
        jsondata = response.json()

        InfoProduct.objects.all().delete()

        for product in jsondata:
            price = float(product['price'])
            sellprice = price * 1.2

            serializer = InfoProductSerializer(data={
                'tig_id': str(product['id']),
                'name': str(product['name']),
                'category': str(product['category']),
                'price': str(price),   
                'unit': str(product['unit']),
                'availability': str(product['availability']),
                'sale': str(product['sale']),
                'discount': str(product['discount']),
                'comments': str(product['comments']),
                'owner': str(product['owner']),
                'quantityInStock': '0', 
                'sellprice': str(sellprice) 
            })

            if serializer.is_valid():
                serializer.save()
                self.stdout.write(self.style.SUCCESS(f'[{time.ctime()}] Successfully added product id="{product["id"]}"'))
            else:
                self.stdout.write(self.style.ERROR(f'[{time.ctime()}] Failed to add product id="{product["id"]}"'))

        self.stdout.write('[' + time.ctime() + '] Data refresh terminated.')
