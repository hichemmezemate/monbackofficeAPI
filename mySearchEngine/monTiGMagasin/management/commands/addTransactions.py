from django.core.management.base import BaseCommand
from django.utils import timezone
from monTiGMagasin.models import Transactions, InfoProduct
import random
from datetime import date, datetime


class Command(BaseCommand):
    help = 'Générer des transactions mensuelles pour 2024 (entier) et 2025 (jusqu\'à aujourd\'hui) en utilisant les produits de InfoProduct'

    def handle(self, *args, **kwargs):
        Transactions.objects.all().delete()

        products = InfoProduct.objects.all()

        if not products.exists():
            self.stdout.write(self.style.WARNING("Aucun produit trouvé dans InfoProduct."))
            return

        transaction_types = ['AJOUT', 'VENTE', 'PERTE']

        today = date.today()
        current_year = today.year
        current_month = today.month

        for year in [2024, 2025]:
            max_month = 12 if year == 2024 else current_month
            for month in range(1, max_month + 1):
                num_transactions = random.randint(6, 10) 
                for _ in range(num_transactions):
                    product = random.choice(products)
                    transaction_type = random.choice(transaction_types)
                    quantity = random.randint(1, 15)

                    price = product.sellprice if transaction_type == 'VENTE' else product.price

                    if transaction_type == 'PERTE':
                        total = 0
                    else:
                        total = round(price * quantity, 2)

                    if transaction_type == 'AJOUT':
                        total = -total

                    day = random.randint(1, 28)
                    date_transaction = datetime(year, month, day)

                    Transactions.objects.create(
                        date_transaction=date_transaction,
                        productId=product.id,
                        productName=product.name,
                        type_transaction=transaction_type,
                        quantity=quantity,
                        price=price,
                        total=total
                    )

        self.stdout.write(self.style.SUCCESS('Transactions générées pour 2024 (tous mois) et 2025 (jusqu\'à aujourd\'hui) à partir des produits InfoProduct.'))
