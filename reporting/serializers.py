from rest_framework import serializers

from reporting.models import Recording, Ticket


class RecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recording


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
