from rest_framework import serializers

class TrainRequestSerializer(serializers.Serializer):
    store_id = serializers.IntegerField(required=True)

class ForecastRequestSerializer(serializers.Serializer):
    store_id = serializers.IntegerField(required=True)
    forecast_days = serializers.IntegerField(default=30, min_value=1, max_value=365)
