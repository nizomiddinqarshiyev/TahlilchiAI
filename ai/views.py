from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TrainRequestSerializer, ForecastRequestSerializer
from .train import train_model
from .forecast import forecast_model


class TrainAPIView(APIView):
    """Modelni o‘qitish uchun endpoint"""
    def post(self, request):
        serializer = TrainRequestSerializer(data=request.data)
        if serializer.is_valid():
            store_id = serializer.validated_data['store_id']
            try:
                train_model(store_id=store_id)
                return Response({
                    "status": "success",
                    "message": f"Store ID {store_id} uchun model(lar) o‘qitildi."
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForecastAPIView(APIView):
    """Modeldan foydalanib bashorat yaratish uchun endpoint"""
    def post(self, request):
        serializer = ForecastRequestSerializer(data=request.data)
        if serializer.is_valid():
            store_id = serializer.validated_data['store_id']
            forecast_days = serializer.validated_data['forecast_days']
            try:
                forecast_model(store_id=store_id, forecast_days=forecast_days)
                return Response({
                    "status": "success",
                    "message": f"{store_id}-store uchun {forecast_days} kunlik bashorat yaratildi."
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
