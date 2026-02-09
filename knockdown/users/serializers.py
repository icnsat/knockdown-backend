from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'theme', 'language', 'keyboard_layout',
            'last_login', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    re_password = serializers.CharField(write_only=True)

    # email is not required
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'password', 're_password',
            'theme', 'language', 'keyboard_layout',
            'last_login', 'date_joined'
        ]
        read_only_fields = ['id', 'last_login', 'date_joined']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('re_password'):
            raise serializers.ValidationError(
                {"password": "Passwords don't match"}
            )
        return attrs
