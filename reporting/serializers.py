from rest_framework import serializers

from reporting.models import Recording, Ticket


class RecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recording


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket


class ReportProblemSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    toilet_id = serializers.CharField(max_length=100)
    category_index = serializers.IntegerField()
    problem_index = serializers.IntegerField()
