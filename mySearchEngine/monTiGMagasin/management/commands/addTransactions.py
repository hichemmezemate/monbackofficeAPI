from django.core.management.base import BaseCommand
from django.utils import timezone
from monTiGMagasin.models import Transactions, InfoProduct  
import random
from datetime import date, timedelta, datetime

class Command(BaseCommand):
    help = 'Générer des transactions'

    def handle(self, *args, **kwargs):
        Transactions.objects.all().delete()  # Clear previous data

        # List of products (including sellprice for "VENTE" transactions)
        products = [
            {"id": 12, "name": "Aile de raie", "price": 10.0, "sellprice": 12.0},
            {"id": 9, "name": "Araignées", "price": 7.0, "sellprice": 8.4},
            {"id": 3, "name": "Bar de ligne", "price": 30.0, "sellprice": 36.0},
            {"id": 2, "name": "Bar de ligne portion", "price": 10.0, "sellprice": 12.0},
            {"id": 10, "name": "Bouquets cuits", "price": 8.0, "sellprice": 9.6},
            {"id": 1, "name": "Filet Bar de ligne", "price": 7.0, "sellprice": 8.4},
            {"id": 5, "name": "Filet Julienne", "price": 19.0, "sellprice": 22.8},
            {"id": 7, "name": "Huitres N°2 St Vaast", "price": 9.5, "sellprice": 11.4},
            {"id": 8, "name": "Huitres N°2 St Vaast", "price": 38.0, "sellprice": 45.6},
            {"id": 13, "name": "Huîtres N°2 OR St Vaast", "price": 12.0, "sellprice": 14.4},
            {"id": 14, "name": "Huîtres N°2 OR St Vaast", "price": 24.0, "sellprice": 28.8},
            {"id": 15, "name": "Huîtres N°2 OR St Vaast", "price": 48.0, "sellprice": 57.6},
            {"id": 16, "name": "Huîtres N°2 St Vaast", "price": 19.0, "sellprice": 22.8},
            {"id": 4, "name": "Lieu jaune de ligne", "price": 12.0, "sellprice": 14.4},
            {"id": 6, "name": "Moules de pêche", "price": 7.0, "sellprice": 8.4}
        ]

        transaction_types = ['AJOUT', 'VENTE', 'PERTE']

        for _ in range(100):
            product = random.choice(products)
            transaction_type = random.choice(transaction_types)
            quantity = random.randint(1, 15)

            # Determine price based on the transaction type
            if transaction_type == 'VENTE':
                price = product['sellprice']
            else:
                price = product['price']

            # If the transaction is "PERTE", set the total to 0
            if transaction_type == 'PERTE':
                total = 0
            else:
                total = round(price * quantity, 2)

            # If it's an "AJOUT" type, make the total negative
            if transaction_type == 'AJOUT':
                total = -total

            # ✅ Generate a new random date for EACH transaction
            random_days = random.randint(0, 180)
            random_date = date.today() - timedelta(days=random_days)
            date_transaction = datetime.combine(random_date, datetime.min.time())

            # Create transaction with productName and selected price
            Transactions.objects.create(
                date_transaction=date_transaction,
                productId=product['id'],
                productName=product['name'],  # Add the product name to the transaction
                type_transaction=transaction_type,
                quantity=quantity,
                price=price,
                total=total
            )

        self.stdout.write(self.style.SUCCESS('Transactions générées avec succès'))

# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from monTiGMagasin.models import Transactions  
# import random
# from datetime import timedelta

# class Command(BaseCommand):
#     help = 'generer des transactions'



#     def handle(self, *args, **kwargs):
#         Transactions.objects.all().delete()
#         products = [
#             {"id": 12, "name": "Aile de raie", "price": 10.0},
#             {"id": 9, "name": "Araignées", "price": 7.0},
#             {"id": 3, "name": "Bar de ligne", "price": 30.0},
#             {"id": 2, "name": "Bar de ligne portion", "price": 10.0},
#             {"id": 10, "name": "Bouquets cuits", "price": 8.0},
#             {"id": 1, "name": "Filet Bar de ligne", "price": 7.0},
#             {"id": 5, "name": "Filet Julienne", "price": 19.0},
#             {"id": 7, "name": "Huitres N°2 St Vaast", "price": 9.5},
#             {"id": 8, "name": "Huitres N°2 St Vaast", "price": 38.0},
#             {"id": 13, "name": "Huîtres N°2 OR St Vaast", "price": 12.0},
#             {"id": 14, "name": "Huîtres N°2 OR St Vaast", "price": 24.0},
#             {"id": 15, "name": "Huîtres N°2 OR St Vaast", "price": 48.0},
#             {"id": 16, "name": "Huîtres N°2 St Vaast", "price": 19.0},
#             {"id": 4, "name": "Lieu jaune de ligne", "price": 12.0},
#             {"id": 6, "name": "Moules de pêche", "price": 7.0}
#         ]
#         transaction_types = ['AJOUT', 'VENTE', 'PERTE']

#         for _ in range(100):
#             product = random.choice(products)
#             transaction_type = random.choice(transaction_types)
#             quantity = random.randint(1, 15)

#             if transaction_type == 'PERTE':
#                 price = 0
#             else:
#                 price = product['price']

#             total = round(price * quantity, 2)
#             if transaction_type == 'AJOUT':
#                 total = -total

#             date_transaction = timezone.now() - timedelta(days=random.randint(0, 180))

#             Transactions.objects.create(
#                 date_transaction=date_transaction,
#                 productId=product['id'],
#                 type_transaction=transaction_type,
#                 quantity=quantity,
#                 price=price,
#                 total=total
#             )

#         self.stdout.write(self.style.SUCCESS('Transactions generées avec succes'))
