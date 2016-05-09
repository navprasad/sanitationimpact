from rest_framework import serializers

from administration.models import Admin, ProblemCategory, Problem, Toilet


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
    email = serializers.CharField(max_length=254, allow_blank=True)
    phone_number = serializers.CharField(max_length=30)
    address = serializers.CharField()
