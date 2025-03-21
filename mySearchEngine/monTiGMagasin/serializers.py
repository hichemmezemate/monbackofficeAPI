from rest_framework.serializers import ModelSerializer
from monTiGMagasin.models import InfoProduct, Transactions

class InfoProductSerializer(ModelSerializer):
    class Meta:
        model = InfoProduct
        fields = ('id', 'tig_id', 'name', 'category', 'price', 'sellprice',  'unit', 'availability', 'sale', 'discount', 'comments', 'owner', 'quantityInStock')

class TransactionsSerializer(ModelSerializer):
    class Meta:
        model = Transactions
        fields = ('id', 'date_transaction', 'productId', 'productName', 'type_transaction', 'quantity', 'price', 'total')
