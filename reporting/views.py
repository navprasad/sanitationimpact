import os
import urllib2

from django.conf import settings
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

        providers = Provider.objects.filter(toilets__toilet_id=toilet_id, problems__id=problem.id)
        if not providers:
            return Response({'success': False, 'error': "No provider found for the Toilet/Problem"})
        provider = providers[0]

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

        # send sms to the provider
        message = "Complaint registered for Toilet ID: " + str(toilet_id) + ". Ticket ID: " + str(ticket.id)
        params = "phone_no=" + provider.phone_number + "&api_key=" + api_key + "&message=" + quote(message, safe='')
        url = url_root + params
        urllib2.urlopen(url).read()

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


class DownloadAudio(APIView):
    def post(self, request):
        ticket_id = request.data.get('ticket_id')
        audio_file_url = request.data.get('audio_file_url')

        if not ticket_id or not audio_file_url:
            return Response({'success': False, 'error': "Invalid POST data"})

        try:
            # ticket = Ticket.objects.get(ticket_id=ticket_id)
            ticket = Ticket.objects.get(pk=ticket_id)
        except (Ticket.DoesNotExist, Ticket.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Ticket ID"})

        try:
            audio_file = urllib2.urlopen(audio_file_url)
        except ValueError:
            return Response({'success': False, 'error': "Invalid URL"})

        file_name = os.path.basename('ticket_' + str(ticket.id) + '_audio.mp3')
        full_file_path = os.path.join(settings.MEDIA_ROOT, "ticket_audio_files", file_name)
        if not os.path.exists(os.path.dirname(full_file_path)):
            os.makedirs(os.path.dirname(full_file_path))
        with open(full_file_path, "wb") as local_file:
            local_file.write(audio_file.read())

        return Response({'success': True})


class GetAudioURL(APIView):
    def post(self, request):
        ticket_id = request.data.get('ticket_id')

        if not ticket_id:
            return Response({'success': False, 'error': "Invalid POST data"})

        try:
            # ticket = Ticket.objects.get(ticket_id=ticket_id)
            ticket = Ticket.objects.get(pk=ticket_id)
        except (Ticket.DoesNotExist, Ticket.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Ticket ID"})

        file_name = os.path.basename('ticket_' + str(ticket.id) + '_audio.mp3')
        full_file_path = os.path.join(settings.MEDIA_ROOT, "ticket_audio_files", file_name)
        if not os.path.isfile(full_file_path):
            return Response({'success': False, 'error': "Audio file does not exist"})

        audio_file_url = '/media/ticket_audio_files/'+file_name
        return Response({'success': True, 'audio_file_url': audio_file_url})
