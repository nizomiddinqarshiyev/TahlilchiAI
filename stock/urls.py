from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StoreViewSet, ProductViewSet, DailySaleViewSet,
    StockDataViewSet, ForecastViewSet, ReplenishmentViewSet
)

router = DefaultRouter()
router.register(r'stores', StoreViewSet)
router.register(r'products', ProductViewSet)
router.register(r'daily-sales', DailySaleViewSet)
router.register(r'stock-data', StockDataViewSet)
router.register(r'forecasts', ForecastViewSet)
router.register(r'replenishments', ReplenishmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
