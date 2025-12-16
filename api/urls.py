from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TodoViewSet, RegisterView, LoginView

urlpatterns = [
    path("auth/signup/", RegisterView.as_view(), name="signup"),
    path("auth/login/", LoginView.as_view(), name="login"),
]
router = DefaultRouter()
router.register(r"todos", TodoViewSet, basename="todo")

urlpatterns += router.urls
