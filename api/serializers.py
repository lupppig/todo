from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Todo, User
from django.utils import timezone


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            email=data["email"],
            password=data["password"],
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        data["user"] = user
        return data


class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )

    def validate_due_at(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Due time must be now or in the future.")
        return value

    def validate_expires_at(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Expiration time must be now or in the future."
            )
        return value

    def validate(self, data):
        due = data.get("due_at")
        expires = data.get("expires_at")
        if due and expires and due > expires:
            raise serializers.ValidationError(
                "Due time cannot be after expiration time."
            )
        return data
