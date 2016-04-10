from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from administration.models import Toilet, Problem
from reporting.models import Recording, Ticket
from reporting.serializers import RecordingSerializer, ReportProblemSerializer, TicketSerializer


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
        except (Toilet.DoesNotExist, Toilet.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Toilet ID"})
        return Response({'success': True})


class ReportProblem(APIView):
    def post(self, request):
        serializer = ReportProblemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
        phone_number = serializer.validated_data['phone_number']
        toilet_id = serializer.validated_data['toilet_id']
        category_index = serializer.validated_data['category_index']
        problem_index = serializer.validated_data['problem_index']

        try:
            toilet = Toilet.objects.get(toilet_id=toilet_id)
            problem = Problem.objects.get(index=problem_index, category__index=category_index)
        except (Toilet.DoesNotExist, Toilet.MultipleObjectsReturned, Problem.DoesNotExist,
                Problem.MultipleObjectsReturned):
            return Response({'success': False})

        # TODO: handle update ticket
        ticket = Ticket(phone_number=phone_number, toilet=toilet, problem=problem)
        ticket.save()

        # TODO: send sms to phone_number
        # TODO: find all providers for the problem for the toilet, and send sms to their phone_number

        return Response({'success': True, 'ticket_id': ticket.id})
