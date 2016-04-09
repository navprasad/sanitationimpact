from rest_framework import viewsets

from reporting.models import Recording, Ticket
from reporting.serializers import RecordingSerializer, TicketSerializer


class RecordingViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
