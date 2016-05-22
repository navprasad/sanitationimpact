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
    pin_code = serializers.CharField(max_length=10)
    email = serializers.CharField(max_length=254, allow_blank=True)
    phone_number = serializers.CharField(max_length=30)
    address = serializers.CharField()


class AddProviderSerializer(serializers.Serializer):
    provider_id = serializers.CharField(max_length=30)  # will act as username
    pin_code = serializers.CharField(max_length=10)  # will act as password
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30, allow_blank=True)
    email = serializers.CharField(max_length=254, allow_blank=True)
    phone_number = serializers.CharField(max_length=30)
    address = serializers.CharField()
    manager = serializers.RelatedField(queryset=Manager.objects.all())

    # manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    # toilets = models.ManyToManyField(Toilet, related_name='providers')
    # problems = models.ManyToManyField(Problem, related_name='providers')
