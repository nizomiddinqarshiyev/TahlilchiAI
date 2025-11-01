import jwt
from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token as AuthToken
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from .permissions import IsAdmin, IsManagerOfOwnStore
from dotenv import load_dotenv

load_dotenv()

SECRET = load_dotenv('SECRET')

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'create', 'destroy']:
            permission_classes = [IsAdmin]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [IsAdmin | IsManagerOfOwnStore]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]


from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer