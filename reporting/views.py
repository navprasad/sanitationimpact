import urllib2
from requests.utils import quote
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

        # send sms to the phone_number
        message = "Your complaint have been registered. Ticket ID: " + str(ticket.id)
        api_key = "KK48377d55790faf6e93f66223c078ced3"
        params = "phone_no=" + phone_number + "&api_key=" + api_key + "&message=" + quote(message, safe='')
        url_root = "http://www.kookoo.in/outbound/outbound_sms.php?"
        url = url_root + params

        urllib2.urlopen(url).read()

        # TODO: find all providers for the problem for the toilet, and send sms to their phone_number

        return Response({'success': True, 'ticket_id': ticket.id})


def is_valid_provider_ticket(provider, ticket):
    if not provider.toilets.filter(pk=ticket.toilet_id).exists():
        return False
    if not provider.problems.filter(pk=ticket.problem_id).exists():
        return False
    return True


class IsValidProviderTicket(APIView):
    def post(self, request):
        provider_id = request.data.get('provider_id', None)
        ticket_id = request.data.get('ticket_id', None)
        if not provider_id or not ticket_id:
            return Response({'success': False, 'error': "Invalid POST data"})
        try:
            provider = Provider.objects.get(provider_id=provider_id)
            # ticket = Ticket.objects.get(ticket_id=ticket_id)
            ticket = Ticket.objects.exclude(status=Ticket.FIXED).get(pk=ticket_id)
        except (Provider.DoesNotExist, Provider.MultipleObjectsReturned, Ticket.DoesNotExist,
                Ticket.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Provider/Ticket"})
        if not is_valid_provider_ticket(provider, ticket):
            return Response({'success': False, 'error': "Toilet/Problem not associated with the Provider"})
        return Response({'success': True})


class ReportFix(APIView):
    def post(self, request):
        serializer = ReportFixSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'error': serializer.errors})
        provider_id = serializer.validated_data['provider_id']
        pin_code = serializer.validated_data['pin_code']
        ticket_id = int(serializer.validated_data['ticket_id'])
        validity_checked = serializer.validated_data['validity_checked']

        try:
            # ticket = Ticket.objects.exclude(status=Ticket.FIXED).get(ticket_id=ticket_id)
            ticket = Ticket.objects.exclude(status=Ticket.FIXED).get(pk=ticket_id)
            provider = Provider.objects.get(provider_id=provider_id, pin_code=pin_code)
        except (Ticket.DoesNotExist, Ticket.MultipleObjectsReturned, Provider.DoesNotExist,
                Provider.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Ticket/Provider"})

        if not validity_checked and not is_valid_provider_ticket(provider, ticket):
            return Response({'success': False, 'error': "Toilet/Problem not associated with the Provider"})

        ticket.status = Ticket.FIXED
        ticket.save()

        # TODO: Send SMS to users and providers/managers based on level of escalation
        return Response({'success': True})
