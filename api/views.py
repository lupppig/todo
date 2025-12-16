from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Todo
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema


from .serializers import RegisterSerializer, LoginSerializer, TodoSerializer


class RegisterView(APIView):
    serializer_class = RegisterSerializer

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "email": user.email,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "email": user.email,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Todo.objects.none()

        queryset = Todo.objects.filter(created_by=self.request.user)
        now = timezone.now()
        for todo in queryset:
            if todo.expires_at and todo.expires_at < now and todo.status != "completed":
                todo.status = "expired"
                todo.save()
        return queryset
