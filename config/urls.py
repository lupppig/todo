from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Todo API",
        default_version="v1",
        description="Simple CRUD Todo API using Django REST Framework",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=(JWTAuthentication,),
)

API_VERSION = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{API_VERSION}", include("api.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),
]
