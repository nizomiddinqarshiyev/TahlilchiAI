from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.permissions import IsAdmin, IsOwnerStoreUser
from .serializers import TrainRequestSerializer, ForecastRequestSerializer
from .train import train_model
from .forecast import forecast_model
from users.models import User
import config

class TrainAPIView(APIView):
    permission_classes = [IsAdmin,]
    """Modelni o‘qitish uchun endpoint"""
    def post(self, request):
        serializer = TrainRequestSerializer(data=request.data)
        user = request.user
        if serializer.is_valid():
            store_id = serializer.validated_data['store_id']
            if user.cache is None or user.cache < config.TRAIN_COST:
                return Response({
                    "status": "error",
                    "message": f"Yetarli balans (cash) mavjud emas. Kamida {config.TRAIN_COST} coin kerak."
                }, status=status.HTTP_403_FORBIDDEN)
            try:
                res = train_model(store_id=store_id)
                user.cache = user.cache - config.TRAIN_COST
                user.save(update_fields=['cache'])
                return Response({
                    "status": "success",
                    "message": f"{res}"
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "status": "error",
                    "message": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForecastAPIView(APIView):
    """Modeldan foydalanib bashorat yaratish uchun endpoint"""
    permission_classes = [IsAuthenticated, IsOwnerStoreUser]

    def post(self, request):
        serializer = ForecastRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        store_id = serializer.validated_data['store_id']
        forecast_days = serializer.validated_data['forecast_days']
        user = request.user
        if store_id is None:
            store_id = user.store_id
        # 🔒 Faqat cash ≥ 3 bo‘lsa bashoratga ruxsat beramiz
        if user.cache is None or user.cache < config.FORECAST_COST:
            return Response({
                "status": "error",
                "message": f"Yetarli balans (cache) mavjud emas. Kamida {config.FORECAST_COST}birlik kerak."
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            # ✅ Modelni ishga tushirish
            res = forecast_model(store_id=store_id, forecast_days=forecast_days)
            # ✅ User cache ni 3 taga kamaytirish
            user.cache = user.cache - config.FORECAST_COST
            user.save(update_fields=['cache'])

            return Response({
                "status": "success",
                "message": f"{res}",
                "new_cache": user.cache
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
