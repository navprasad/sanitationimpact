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
