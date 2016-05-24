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
    audio_file_url = serializers.CharField(max_length=255, required=False)


class ReportFixSerializer(serializers.Serializer):
    provider_id = serializers.CharField(max_length=100)
    pin_code = serializers.CharField(max_length=10)
    ticket_id = serializers.CharField(max_length=40)
    validity_checked = serializers.BooleanField(default=False)
