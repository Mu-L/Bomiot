from rest_framework import serializers
from django.contrib.auth import get_user_model
from bomiot.server.core import models

User = get_user_model()


class ExampleSerializer(serializers.ModelSerializer):
    """
    Example Serializer
    """
    data = serializers.JSONField(read_only=True, required=False)
    project = serializers.CharField(read_only=True, required=False)
    is_delete = serializers.BooleanField(read_only=True, required=False)
    created_time = serializers.DateTimeField(read_only=True, required=False, format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(read_only=True, required=False, format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = models.Example
        fields = ['id', 'data', 'project', 'is_delete', 'created_time', 'updated_time']
        read_only_fields = ['id']
