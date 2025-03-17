from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from monTiGMagasin.config import baseUrl
from monTiGMagasin.models import InfoProduct, Transactions
from monTiGMagasin.serializers import InfoProductSerializer, TransactionsSerializer
from django.db.models import Sum, F
from rest_framework import status
from django.db.models.functions import ExtractMonth, ExtractYear
from datetime import datetime

#######################
#...TME3 JWT starts...#
from rest_framework.permissions import IsAuthenticated
#...end of TME3 JWT...#
#######################

# Create your views here.
class InfoProductList(APIView):
#######################
#...TME3 JWT starts...#
    # permission_classes = (IsAuthenticated,)
#...end of TME3 JWT...#
#######################
    def get(self, request, format=None):
        products = InfoProduct.objects.all()
        serializer = InfoProductSerializer(products, many=True)
        return Response(serializer.data)
class InfoProductDetail(APIView):
#######################
#...TME3 JWT starts...#
    permission_classes = (IsAuthenticated,)
#...end of TME3 JWT...#
#######################
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

        # Apply filters
        if year:
            transactions = transactions.annotate(year=ExtractYear('date_transaction')).filter(year=year)
        if month:
            transactions = transactions.annotate(month=ExtractMonth('date_transaction')).filter(month=month)

        # GROUPING LOGIC
        if year and month:
            # Monthly Resume
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
            # Yearly Resume
            transactions = transactions.annotate(year=ExtractYear('date_transaction'))
            grouped = transactions.values('year', 'type_transaction').annotate(total=Sum('total'))

            for item in grouped:
                key = str(item['year'])
                if key not in summary:
                    summary[key] = self._init_summary()
                self._update_summary(summary[key], item)

        else:
            # Global Resume (no filters)
            grouped = transactions.values('type_transaction').annotate(total=Sum('total'))
            key = "global"
            summary[key] = self._init_summary()

            for item in grouped:
                self._update_summary(summary[key], item)

        # Final calculations
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

        # Filter if year or month is provided
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

        # Calculate argent_net
        for key in summary:
            summary[key]['chiffre_affaire'] = round(summary[key]['chiffre_affaire'], 2)
            summary[key]['depenses'] = round(summary[key]['depenses'], 2)
            summary[key]['pertes'] = round(summary[key]['pertes'], 2)
            summary[key]['argent_net'] = round(summary[key]['chiffre_affaire'] - summary[key]['depenses'], 2)

        return Response(summary, status=status.HTTP_200_OK)


# class ResumeFinancierView2(APIView):
#     def get(self, request):
#         year = request.GET.get('year')
#         month = request.GET.get('month')

#         # Default response structure
#         summary = {}

#         if not year:
#             return Response({"error": "Year is required"}, status=400)

#         # Get all transactions, optionally filter by year and month
#         transactions = Transactions.objects.all()

#         print("Transactions : ", transactions)

#         # Apply filters if year or month is provided
#         if year:
#             transactions = transactions.annotate(year=ExtractYear('date_transaction')).filter(year=year)
#         if month:
#             transactions = transactions.annotate(month=ExtractMonth('date_transaction')).filter(month=month)

#         # Grouping and summarizing data
#         if year and month:
#             # Monthly Resume (Year and Month)
#             transactions = transactions.annotate(year=ExtractYear('date_transaction'), month=ExtractMonth('date_transaction'))
#             grouped = transactions.values('year', 'month', 'type_transaction').annotate(total=Sum('total'))

#             for item in grouped:
#                 key = f"{item['year']}-{item['month']:02d}"
#                 if key not in summary:
#                     summary[key] = self._init_summary()
#                 self._update_summary(summary[key], item)

#         elif year:
#             # Yearly Resume (Year Only)
#             transactions = transactions.annotate(year=ExtractYear('date_transaction'))
#             grouped = transactions.values('year', 'type_transaction').annotate(total=Sum('total'))

#             for item in grouped:
#                 key = str(item['year'])
#                 if key not in summary:
#                     summary[key] = self._init_summary()
#                 self._update_summary(summary[key], item)

#         else:
#             # Global Resume (No filters)
#             grouped = transactions.values('type_transaction').annotate(total=Sum('total'))
#             key = "global"
#             summary[key] = self._init_summary()

#             for item in grouped:
#                 self._update_summary(summary[key], item)

#         # Ensure all months (1 to 12) are included for the requested year, even if no data for some months
#         if year:
#             for month_num in range(1, 13):  # Loop through all 12 months
#                 month_key = f"{year}-{month_num:02d}"
#                 if month_key not in summary:
#                     summary[month_key] = self._init_summary()

#         # Final calculations and rounding
#         for data in summary.values():
#             data['chiffre_affaire'] = round(data['chiffre_affaire'], 2)
#             data['depenses'] = round(data['depenses'], 2)
#             data['pertes'] = round(data['pertes'], 2)
#             data['argent_net'] = round(data['chiffre_affaire'] - data['depenses'], 2)

#         return Response(summary, status=200)

#     def _init_summary(self):
#         """Initialize summary for a specific month"""
#         return {
#             'chiffre_affaire': 0.0,
#             'depenses': 0.0,
#             'pertes': 0.0,
#             'argent_net': 0.0,
#         }

#     def _update_summary(self, target, item):
#         """Update the summary for each transaction type"""
#         total = item['total'] or 0.0
#         if item['type_transaction'] == 'VENTE':
#             target['chiffre_affaire'] += total
#         elif item['type_transaction'] == 'AJOUT':
#             target['depenses'] += abs(total)
#         elif item['type_transaction'] == 'PERTE':
#             target['pertes'] += total