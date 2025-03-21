from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from monTiGMagasin.config import baseUrl
from monTiGMagasin.models import InfoProduct, Transactions
from monTiGMagasin.serializers import InfoProductSerializer, TransactionsSerializer
from django.db.models import Sum, F
from rest_framework import status
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated

class InfoProductList(APIView):
    def get(self, request, format=None):
        products = InfoProduct.objects.all()
        serializer = InfoProductSerializer(products, many=True)
        return Response(serializer.data)
class InfoProductDetail(APIView):
    permission_classes = (IsAuthenticated,)
    def get_object(self, tig_id):
        try:
            return InfoProduct.objects.get(tig_id=tig_id)
        except InfoProduct.DoesNotExist:
            raise Http404
    def get(self, request, tig_id, format=None):
        product = self.get_object(tig_id=tig_id)
        serializer = InfoProductSerializer(product)
        return Response(serializer.data)


class InfoProductListPoissons(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        poissonList = []
        products = InfoProduct.objects.all()
        for prod in products:
            if prod.category == 0:
                poissonList.append(prod)

        serializer = InfoProductSerializer(poissonList, many=True)
        return Response(serializer.data)

class InfoProductListCrustaces(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        poissonList = []
        products = InfoProduct.objects.all()
        for prod in products:
            if prod.category == 1:
                poissonList.append(prod)

        serializer = InfoProductSerializer(poissonList, many=True)
        return Response(serializer.data)

class InfoProductListFruitsDeMer(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        poissonList = []
        products = InfoProduct.objects.all()
        for prod in products:
            if prod.category == 2:
                poissonList.append(prod)

        serializer = InfoProductSerializer(poissonList, many=True)
        return Response(serializer.data)

class TransactionsList(APIView):
    def get(self, request, format=None):
        transactions = Transactions.objects.all()
        serializer = TransactionsSerializer(transactions, many=True)
        return Response(serializer.data)


class ResumeFinancierView(APIView):
    def get(self, request):
        year = request.GET.get('year')
        month = request.GET.get('month')

        transactions = Transactions.objects.all()
        summary = {}

        if year:
            transactions = transactions.annotate(year=ExtractYear('date_transaction')).filter(year=year)
        if month:
            transactions = transactions.annotate(month=ExtractMonth('date_transaction')).filter(month=month)

        if year and month:
            transactions = transactions.annotate(
                year=ExtractYear('date_transaction'),
                month=ExtractMonth('date_transaction')
            )
            grouped = transactions.values('year', 'month', 'type_transaction').annotate(total=Sum('total'))

            for item in grouped:
                key = f"{item['year']}-{item['month']:02d}"
                if key not in summary:
                    summary[key] = self._init_summary()
                self._update_summary(summary[key], item)

        elif year:
            transactions = transactions.annotate(year=ExtractYear('date_transaction'))
            grouped = transactions.values('year', 'type_transaction').annotate(total=Sum('total'))

            for item in grouped:
                key = str(item['year'])
                if key not in summary:
                    summary[key] = self._init_summary()
                self._update_summary(summary[key], item)

        else:
            grouped = transactions.values('type_transaction').annotate(total=Sum('total'))
            key = "global"
            summary[key] = self._init_summary()

            for item in grouped:
                self._update_summary(summary[key], item)

        for data in summary.values():
            data['chiffre_affaire'] = round(data['chiffre_affaire'], 2)
            data['depenses'] = round(data['depenses'], 2)
            data['pertes'] = round(data['pertes'], 2)
            data['argent_net'] = round(data['chiffre_affaire'] - data['depenses'], 2)

        return Response(summary, status=status.HTTP_200_OK)

    def _init_summary(self):
        return {
            'chiffre_affaire': 0.0,
            'depenses': 0.0,
            'pertes': 0.0,
            'argent_net': 0.0,
        }

    def _update_summary(self, target, item):
        total = item['total'] or 0.0
        if item['type_transaction'] == 'VENTE':
            target['chiffre_affaire'] += total
        elif item['type_transaction'] == 'AJOUT':
            target['depenses'] += abs(total)
        elif item['type_transaction'] == 'PERTE':
            target['pertes'] += total


class ResumeFinancierView2(APIView):
    def get(self, request):
        year = request.GET.get('year')
        month = request.GET.get('month')

        transactions = Transactions.objects.all()

        if year:
            transactions = transactions.annotate(year=ExtractYear('date_transaction')).filter(year=year)
        if month:
            transactions = transactions.annotate(month=ExtractMonth('date_transaction')).filter(month=month)

        transactions = transactions.annotate(
            year=ExtractYear('date_transaction'),
            month=ExtractMonth('date_transaction')
        )

        summary = {}

        for item in transactions.values('year', 'month', 'type_transaction').annotate(total=Sum('total')):
            y = item['year']
            m = item['month']
            type_transaction = item['type_transaction']
            total = item['total'] or 0.0

            key = f"{y}-{m:01d}"
            if key not in summary:
                summary[key] = {
                    'chiffre_affaire': 0.0,
                    'depenses': 0.0,
                    'pertes': 0.0,
                    'argent_net': 0.0,
                }

            if type_transaction == 'VENTE':
                summary[key]['chiffre_affaire'] += total
            elif type_transaction == 'AJOUT':
                summary[key]['depenses'] += abs(total)
            elif type_transaction == 'PERTE':
                summary[key]['pertes'] += total

        for key in summary:
            summary[key]['chiffre_affaire'] = round(summary[key]['chiffre_affaire'], 2)
            summary[key]['depenses'] = round(summary[key]['depenses'], 2)
            summary[key]['pertes'] = round(summary[key]['pertes'], 2)
            summary[key]['argent_net'] = round(summary[key]['chiffre_affaire'] - summary[key]['depenses'], 2)

        return Response(summary, status=status.HTTP_200_OK)
    

class TransactionCountByProductView(APIView):
    def get(self, request):
        year = request.GET.get('year')
        month = request.GET.get('month')
        transaction_type = request.GET.get('type_transaction')

        transactions = Transactions.objects.annotate(
            year=ExtractYear('date_transaction'),
            month=ExtractMonth('date_transaction')
        )

        if year:
            transactions = transactions.filter(year=year)
        if month:
            transactions = transactions.filter(month=month)
        if transaction_type:
            transactions = transactions.filter(type_transaction=transaction_type)

        summary = {}

        if not year and not month:
            transactions = transactions.values('type_transaction', 'productName').annotate(count=Count('id'))
            for item in transactions:
                tx_type = item['type_transaction']
                product = item['productName']
                count = item['count']

                summary.setdefault('global', {}).setdefault(tx_type, {})[product] = count
        else:
            transactions = transactions.values('year', 'month', 'productName', 'type_transaction').annotate(count=Count('id'))
            for item in transactions:
                y = item['year']
                m = item['month']
                tx_type = item['type_transaction']
                product = item['productName']
                count = item['count']

                summary.setdefault(y, {}).setdefault(m, {}).setdefault(tx_type, {})[product] = count

        return Response(summary, status=status.HTTP_200_OK)
