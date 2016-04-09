from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from administration.models import Toilet
from reporting.models import Recording, Ticket
from reporting.serializers import RecordingSerializer, TicketSerializer


class RecordingViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class IsValidToilet(APIView):
    def post(self, request):
        toilet_id = request.data.get('toilet_id', None)
        if not toilet_id:
            return Response({'success': False, 'error': "Invalid POST data"})
        try:
            Toilet.objects.get(toilet_id=toilet_id)
        except (Toilet.DoesNotExist, Toilet.DoesNotExist):
            return Response({'success': False, 'error': "Invalid Toilet ID"})
        return Response({'success': True})
