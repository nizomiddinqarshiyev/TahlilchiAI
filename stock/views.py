from rest_framework import viewsets
from .models import Store, Product, DailySale, StockData, Forecast, Replenishment
from .serializers import (
    StoreSerializer, ProductSerializer, DailySaleSerializer,
    StockDataSerializer, ForecastSerializer, ReplenishmentSerializer
)


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class DailySaleViewSet(viewsets.ModelViewSet):
    queryset = DailySale.objects.all()
    serializer_class = DailySaleSerializer


class StockDataViewSet(viewsets.ModelViewSet):
    queryset = StockData.objects.all()
    serializer_class = StockDataSerializer


class ForecastViewSet(viewsets.ModelViewSet):
    queryset = Forecast.objects.all()
    serializer_class = ForecastSerializer


class ReplenishmentViewSet(viewsets.ModelViewSet):
    queryset = Replenishment.objects.all()
    serializer_class = ReplenishmentSerializer
