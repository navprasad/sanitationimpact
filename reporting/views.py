import os
import urllib2

from django.conf import settings
from administration.views import send_sms
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from administration.models import Toilet, Problem
from manager.models import Manager
from provider.models import Provider
from reporting.models import Ticket
from reporting.serializers import ReportProblemSerializer, ReportFixSerializer, TicketSerializer


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
        audio_file_url = serializer.validated_data.get('audio_file_url')

        try:
            toilet = Toilet.objects.get(toilet_id=toilet_id)
            problem = Problem.objects.get(index=problem_index, category__index=category_index)
        except (Toilet.DoesNotExist, Toilet.MultipleObjectsReturned, Problem.DoesNotExist,
                Problem.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Toilet/Problem"})

        providers = Provider.objects.filter(toilets__toilet_id=toilet_id, problems__id=problem.id)
        if not providers:
            provider = None
        else:
            # TODO: Handle this better
            provider = providers[0]

        # TODO: handle update ticket
        ticket = Ticket(phone_number=phone_number, toilet=toilet, problem=problem, provider=provider)
        ticket.save()

        if problem.category.is_audio_recording:
            if not audio_file_url:
                return Response({'success': False, 'error': "Invalid POST data"})
            file_name = os.path.basename('ticket_' + str(ticket.id) + '_audio.mp3')
            full_file_path = os.path.join(settings.MEDIA_ROOT, "ticket_audio_files", file_name)

            download_response = download_audio(audio_file_url, full_file_path)
            if not download_response['success']:
                ticket.delete()
                return Response(download_response)

        # send sms to the phone_number
        message = "Your complaint have been registered. Ticket ID: " + str(ticket.id)
        send_sms(phone_number, message)

        # send sms to the provider
        if provider:
            message = "Complaint registered for Toilet ID: " + str(toilet_id) + ". Ticket ID: " + str(ticket.id)
            send_sms(provider.user_profile.phone_number, message)

        return Response({'success': True, 'ticket_id': ticket.id})


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
        if ticket.provider != provider:
            return Response({'success': False, 'error': "Toilet/Problem not associated with the Provider"})
        return Response({'success': True})


class IsValidManagerTicket(APIView):
    def post(self, request):
        manager_id = request.data.get('manager_id', None)
        ticket_id = request.data.get('ticket_id', None)
        if not manager_id or not ticket_id:
            return Response({'success': False, 'error': "Invalid POST data"})
        try:
            manager = Manager.objects.get(manager_id=manager_id)
            # ticket = Ticket.objects.get(ticket_id=ticket_id)
            ticket = Ticket.objects.exclude(status=Ticket.FIXED).get(pk=ticket_id)
        except (Manager.DoesNotExist, Manager.MultipleObjectsReturned, Ticket.DoesNotExist,
                Ticket.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Manager/Ticket"})
        if not manager.providers.filter(toilets=ticket.toilet).exists():
            return Response({'success': False, 'error': "Ticket not associated with the Manager"})
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

        if not validity_checked and ticket.provider != provider:
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

        file_name = os.path.basename('ticket_' + str(ticket.id) + '_provider_audio.mp3')
        full_file_path = os.path.join(settings.MEDIA_ROOT, "ticket_audio_files", file_name)

        download_response = download_audio(audio_file_url, full_file_path)
        return Response(download_response)


def download_audio(audio_file_url, full_file_path):
    try:
        audio_file = urllib2.urlopen(audio_file_url)
    except ValueError:
        return {'success': False, 'error': "Invalid audio file URL"}
    if not os.path.exists(os.path.dirname(full_file_path)):
        os.makedirs(os.path.dirname(full_file_path))
    with open(full_file_path, "wb") as local_file:
        local_file.write(audio_file.read())
    return {'success': True}


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

        file_name = os.path.basename('ticket_' + str(ticket.id) + '_provider_audio.mp3')
        full_file_path = os.path.join(settings.MEDIA_ROOT, "ticket_audio_files", file_name)
        if not os.path.isfile(full_file_path):
            return Response({'success': False, 'error': "Audio file does not exist"})

        audio_file_url = '/media/ticket_audio_files/' + file_name
        return Response({'success': True, 'audio_file_url': audio_file_url})
