from rest_framework import viewsets, permissions
from .models import Store, Product, DailySale, StockData, Forecast, Replenishment
from users import permissions as user_permissions
from .serializers import (
    StoreSerializer, ProductSerializer, DailySaleSerializer,
    StockDataSerializer, ForecastSerializer, ReplenishmentSerializer
)


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = StoreSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = ProductSerializer


class DailySaleViewSet(viewsets.ModelViewSet):
    queryset = DailySale.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = DailySaleSerializer


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
