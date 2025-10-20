from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RegisterView, LoginView

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/', include(router.urls)),
]
