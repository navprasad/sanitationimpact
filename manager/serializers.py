from rest_framework import serializers

from manager.models import Manager


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager


class AddManagerSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30, allow_blank=True)
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(allow_blank=True)
    email = serializers.CharField(max_length=254, allow_blank=True)
    phone_number = serializers.CharField(max_length=30)
    address = serializers.CharField()
