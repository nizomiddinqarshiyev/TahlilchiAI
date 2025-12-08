import datetime
import json
from rest_framework import viewsets, permissions
from sqlalchemy.sql.operators import isnot

from ai.forecast import forecast_model
from users import permissions as user_permissions
from users.permissions import IsOwnerStoreUser, IsAdmin
from .serializers import (
    StoreSerializer, ProductSerializer, DailySaleSerializer,
    StockDataSerializer, ForecastSerializer, ReplenishmentSerializer
)


import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Store, Product, DailySale, StockData, Forecast, Replenishment
from .utils import calculate_replenishment


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = StoreSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = (IsOwnerStoreUser,)
    serializer_class = ProductSerializer

class DailySaleViewSet(viewsets.ModelViewSet):
    queryset = DailySale.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = DailySaleSerializer


class DailyTrain(APIView):
    queryset = DailySale.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = DailySaleSerializer
    def post(self, request, format=None):
        forecast_model()


class StockDataViewSet(viewsets.ModelViewSet):
    queryset = StockData.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = StockDataSerializer


class ForecastViewSet(viewsets.ModelViewSet):
    queryset = Forecast.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = ForecastSerializer


class ReplenishmentViewSet(viewsets.ModelViewSet):
    queryset = Replenishment.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = ReplenishmentSerializer

class AutoReplenishmentAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        try:
            store_id = request.user.store_id
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({"error": "Store topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(store_id=store)

        results = []
        for product in products:
            r = calculate_replenishment(store, product)
            results.append(r)

        return Response({
            "store": store.name,
            "total_products": products.count(),
            "replenishment_results": results
        }, status=status.HTTP_201_CREATED)



class FileUploadAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        model_name = request.data.get('model')

        file_obj = request.data.get('file')

        if not file_obj or not model_name:
            return Response(
                {"error": "Iltimos, model nomi va faylni yuboring."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Modelni aniqlash
        model_map = {
            'store': Store,
            'product': Product,
            'dailysale': DailySale,
            'stockdata': StockData,
            'replenishment': Replenishment
        }

        model = model_map.get(model_name.lower())
        if not model:
            return Response(
                {"error": f"'{model_name}' nomli model topilmadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            # Fayl turini aniqlash (Json, Excel yoki CSV)
                if file_obj.name.endswith('.csv'):
                    df = pd.read_csv(file_obj)

                elif file_obj.name.endswith('.json'):
                    data = json.load(file_obj)
                    if isinstance(data, dict):
                        # Agar JSON bitta obyekt bo‘lsa
                        data = [data]
                    df = pd.DataFrame(data)
                else:
                    df = pd.read_excel(file_obj)
        except Exception as e:
            return Response({"error": f"Faylni o‘qishda xatolik: {e}"}, status=400)

        # Ma’lumotlarni bazaga joylash
        created_count = 0
        if model_name.lower() == 'dailysale':
            store_id = request.data.get('store_id')
            for _, row in df.iterrows():
                data = row.to_dict()
                try:
                    format_string = "%Y-%m-%d %H:%M:%S"
                    model.objects.create(
                    sale_date=datetime.datetime.strptime(data['date'], "%d/%m/%Y"),
                    product_id=data['product_id'],
                    quantity=data['quantity'],
                    store_id=store_id)
                    created_count += 1
                except Exception as e:
                    print(f"⚠️ Xatolik: {e}")
        else:
            for _, row in df.iterrows():
                data = row.to_dict()
                try:
                    model.objects.create(**data)
                    created_count += 1
                except Exception as e:
                    print(f"⚠️ Xatolik: {e}")

        return Response({
            "message": f" {created_count} ta {model_name} muvaffaqiyatli yuklandi."
        }, status=200)

class UploadForecastAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        file_obj = request.data.get('file')
        store_id = request.data.get('store_id')
        period = request.data.get('period')
        if not file_obj or not store_id or not period:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            if file_obj.name.endswith('.json'):
                data = json.load(file_obj)
                arr = []
                for k, v in data.items():
                    product_id = v['product_id']
                    forecast = v['forecast']

                    for fcst in forecast:
                        dic = {
                            'product_id': product_id,
                            'forecast_date': fcst['date'],
                            'predicted_quantity': fcst['predicted_quantity'],
                            'forecast_period': period,
                            'store_id': store_id
                        }

                        arr.append(dic)
                df = pd.DataFrame(arr)
            else:
            # Fayl turini aniqlash (Json, Excel yoki CSV)
                if file_obj.name.endswith('.csv'):
                    df = pd.read_csv(file_obj)
                else:
                    df = pd.read_excel(file_obj)
        except Exception as e:
            return Response({"error": f"Faylni o‘qishda xatolik: {e}"}, status=400)

        # Ma’lumotlarni bazaga joylash
        created_count = 0
        for _, row in df.iterrows():
            data = row.to_dict()
            try:
                Forecast.objects.create(**data)
                created_count += 1
            except Exception as e:
                print(f"⚠️ Xatolik: {e}")

        return Response({
            "message": f"{created_count} ta forecast  muvaffaqiyatli yuklandi."
        }, status=200)