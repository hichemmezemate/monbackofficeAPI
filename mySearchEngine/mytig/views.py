import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from mytig.config import baseUrl
from rest_framework.permissions import IsAuthenticated
import json
from rest_framework.reverse import reverse
from django.http import Http404
from rest_framework import renderers
from mytig.models import ProduitEnPromotion
from monTiGMagasin.models import InfoProduct, Transactions
from monTiGMagasin.serializers import InfoProductSerializer
from mytig.serializers import ProduitEnPromotionSerializer
from rest_framework import status
from django.utils import timezone


class RedirectionListeDeProduits(APIView):
    def get(self, request, format=None):
        response = requests.get(baseUrl+'products/')
        jsondata = response.json()
        return Response(jsondata)
    
class RedirectionDetailProduit(APIView):
    def get_object(self, pk):
        try:
            response = requests.get(baseUrl+'product/'+str(pk)+'/')
            jsondata = response.json()
            return Response(jsondata)
        except:
            raise Http404
    def get(self, request, pk, format=None):
        response = requests.get(baseUrl+'product/'+str(pk)+'/')
        jsondata = response.json()
        return Response(jsondata)

class JPEGRenderer(renderers.BaseRenderer):
    media_type = 'image/jpeg'
    format = 'jpg'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data

class ProduitImageRandom(APIView):
    renderer_classes = [JPEGRenderer]
    def get(self, request, pk, format=None):
        try:
            projectUrl = reverse('projectRoot',request=request, format=format)
            response = requests.get(json.loads(requests.get(projectUrl+'myImage/random/').text)['url'])
            return Response(response)
        except:
            raise Http404

class ProduitImage(APIView):
    renderer_classes = [JPEGRenderer]
    def get(self, request, pk, image_id, format=None):
        try:
            projectUrl = reverse('projectRoot',request=request, format=format)
            response = requests.get(json.loads(requests.get(projectUrl+'myImage/'+str(image_id)+'/').text)['url'])
            return Response(response)
        except:
            raise Http404

class PromoList(APIView):
    def get(self, request, format=None):
        res=[]
        for prod in ProduitEnPromotion.objects.all():
            serializer = ProduitEnPromotionSerializer(prod)
            response = requests.get(baseUrl+'product/'+str(serializer.data['tigID'])+'/')
            print("RESPONSE : ", response)
            jsondata = response.json()
            res.append(jsondata)
        return Response(res)

class PromoDetail(APIView):
    def get_object(self, pk):
        try:
            return ProduitEnPromotion.objects.get(pk=pk)
        except ProduitEnPromotion.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        prod = self.get_object(pk)
        serializer = ProduitEnPromotionSerializer(prod)
        response = requests.get(baseUrl+'product/'+str(serializer.data['tigID'])+'/')
        jsondata = response.json()
        return Response(jsondata)
    
class removeSale(APIView):
    def get_object(self, id):
        try:
            return InfoProduct.objects.get(id=id)
        except InfoProduct.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        print("PK : ", id)
        prod = self.get_object(id)
        print("PROD : ", prod)
        if prod.sale: 
            prod.sale = False
            prod.discount = 0.0
            prod.save()

            serializer = InfoProductSerializer(prod)
            print("Serial", str(serializer.data))

            return Response({"message": "Sale removed", "product": serializer.data})
        else:
            return Response({"message": "Product is not on sale"})  

class putOnSale(APIView):
    def get_object(self, id):
        try:
            return InfoProduct.objects.get(id=id)
        except InfoProduct.DoesNotExist:
            raise Http404

    def get(self, request, id, newprice, format=None):
        try:
            newprice = float(newprice)
        except ValueError:
            return Response({"error": "Invalid price format"}, status=400)

        prod = self.get_object(id)

        prod.discount = newprice
        prod.sale = True
        prod.save()

        serializer = InfoProductSerializer(prod)

        return Response({
            "message": "Product is now on sale",
            "product": serializer.data
        })

class editProduct(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, id):
        try:
            return InfoProduct.objects.get(id=id)
        except InfoProduct.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        products = request.data

        if not products:
            return Response({"error": "No products provided"}, status=status.HTTP_400_BAD_REQUEST)

        updated_products = []

        for product in products:
            try:
                product_id = product.get('id')
                new_price = float(product.get('newPrice'))
                new_sellprice = float(product.get('newSellPrice'))
                new_discount = float(product.get('newDiscount'))
                transaction_type = product.get('transactionType')
                edited_quantity = float(product.get('editedQuantity', 0))

                prod = self.get_object(product_id)

                if transaction_type == "AJOUT":
                    prod.quantityInStock += edited_quantity
                elif transaction_type in ["PERTE", "VENTE"]:
                    prod.quantityInStock -= edited_quantity

                if new_price != prod.price:
                    prod.price = new_price

                if new_sellprice != prod.sellprice:
                    prod.sellprice = new_sellprice

                if new_discount != 0:
                    prod.discount = new_discount
                    prod.sale = True
                else:
                    prod.discount = 0
                    prod.sale = False

                prod.save()
                thePrice = 0
                if transaction_type and edited_quantity:
                    if transaction_type == "AJOUT":
                        total = -1 * new_price * edited_quantity
                        thePrice += new_price
                    elif transaction_type == "PERTE":
                        total = 0
                    elif transaction_type == "VENTE":
                        total = new_sellprice * edited_quantity
                        thePrice += new_sellprice
                    else:
                        total = 0

                    Transactions.objects.create(
                        date_transaction=timezone.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                        productId=prod.id,
                        productName=prod.name,
                        type_transaction=transaction_type,
                        quantity=edited_quantity,
                        price=thePrice,
                        total=total
                    )
                else:
                    return Response({"error": "Can't edit the product"}, status=status.HTTP_400_BAD_REQUEST)

                serializer = InfoProductSerializer(prod)
                updated_products.append(serializer.data)

            except ValueError:
                return Response({"error": "Invalid quantity format"}, status=status.HTTP_400_BAD_REQUEST)
            except InfoProduct.DoesNotExist:
                return Response({"error": f"Product with ID {product_id} not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "message": "Updated quantities for products",
            "products": updated_products
        }, status=status.HTTP_200_OK)
