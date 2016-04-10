from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from administration.models import Toilet, Problem
from provider.models import Provider
from reporting.models import Recording, Ticket
from reporting.serializers import RecordingSerializer, ReportProblemSerializer, ReportFixSerializer, TicketSerializer


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
            return Response({'success': False, 'error': serializer.errors})
        phone_number = serializer.validated_data['phone_number']
        toilet_id = serializer.validated_data['toilet_id']
        category_index = serializer.validated_data['category_index']
        problem_index = serializer.validated_data['problem_index']

        try:
            toilet = Toilet.objects.get(toilet_id=toilet_id)
            problem = Problem.objects.get(index=problem_index, category__index=category_index)
        except (Toilet.DoesNotExist, Toilet.MultipleObjectsReturned, Problem.DoesNotExist,
                Problem.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Toilet/Problem"})

        # TODO: handle update ticket
        ticket = Ticket(phone_number=phone_number, toilet=toilet, problem=problem)
        ticket.save()

        # TODO: send sms to phone_number
        # TODO: find all providers for the problem for the toilet, and send sms to their phone_number

        return Response({'success': True, 'ticket_id': ticket.id})


class ReportFix(APIView):
    def post(self, request):
        serializer = ReportFixSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'error': serializer.errors})
        provider_id = serializer.validated_data['provider_id']
        pin_code = serializer.validated_data['pin_code']
        ticket_id = serializer.validated_data['ticket_id']

        try:
            ticket = Ticket.objects.exclude(status=Ticket.FIXED).get(ticket_id=ticket_id)
            provider = Provider.objects.get(provider_id=provider_id, pin_code=pin_code)
        except (Ticket.DoesNotExist, Ticket.MultipleObjectsReturned, Provider.DoesNotExist,
                Provider.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Ticket/Provider"})

        # Check if provider matches the toilet and problem
        if not provider.toilets.filter(pk=ticket.toilet_id).exists():
            return Response({'success': False, 'error': "Toilet/Problem not associated with the Provider"})
        if not provider.problems.filter(pk=ticket.problem_id).exists():
            return Response({'success': False, 'error': "Toilet/Problem not associated with the Provider"})

        ticket.status = Ticket.FIXED
        ticket.save()

        # TODO: Send SMS to users and providers/managers based on level of escalation
        return Response({'success': True})
