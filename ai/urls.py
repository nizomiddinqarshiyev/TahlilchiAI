from django.urls import path
from .views import TrainAPIView, ForecastAPIView

urlpatterns = [
    path('train/', TrainAPIView.as_view(), name='train'),
    path('forecast/', ForecastAPIView.as_view(), name='forecast'),
]
