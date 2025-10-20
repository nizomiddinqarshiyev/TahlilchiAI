from rest_framework import serializers
from .models import Store, Product, DailySale, StockData, Forecast, Replenishment


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class DailySaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySale
        fields = '__all__'


class StockDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = '__all__'


class ForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forecast
        fields = '__all__'


class ReplenishmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Replenishment
        fields = '__all__'
