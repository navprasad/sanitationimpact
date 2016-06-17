from rest_framework import serializers

from administration.models import Admin, ProblemCategory, Problem, Toilet
from manager.models import Manager


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin


class ProblemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProblemCategory


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem


class ToiletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Toilet


class AddManagerSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30, allow_blank=True)
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(allow_blank=True)
    manager_id = serializers.CharField(max_length=100)
    pin_code = serializers.CharField(max_length=10)
    email = serializers.CharField(max_length=254, allow_blank=True)
    phone_number = serializers.CharField(max_length=30)
    address = serializers.CharField()
    description = serializers.CharField(allow_blank=True)


class AddProviderSerializer(serializers.Serializer):
    provider_id = serializers.CharField(max_length=30)  # will act as username
    pin_code = serializers.CharField(max_length=10)  # will act as password
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(allow_blank=True)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30, allow_blank=True)
    email = serializers.CharField(max_length=254, allow_blank=True)
    phone_number = serializers.CharField(max_length=30)
    address = serializers.CharField()
    manager = serializers.PrimaryKeyRelatedField(queryset=Manager.objects.all())
    toilets = serializers.PrimaryKeyRelatedField(queryset=Toilet.objects.all(), many=True)
    problems = serializers.PrimaryKeyRelatedField(queryset=Problem.objects.all(), many=True)
    description = serializers.CharField(allow_blank=True)
    provider_code = serializers.CharField(max_length=5)
