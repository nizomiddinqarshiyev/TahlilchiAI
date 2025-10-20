from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from .serializers import UserSerializer, RegisterSerializer
from .permissions import IsAdmin, IsManagerOfOwnStore

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role,
                }
            })
        return Response({"error": "Login yoki parol noto‘g‘ri!"}, status=400)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'create', 'destroy']:
            permission_classes = [IsAdmin]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [IsAdmin | IsManagerOfOwnStore]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [p() for p in permission_classes]
