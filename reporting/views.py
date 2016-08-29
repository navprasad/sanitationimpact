import os
import urllib2
import json
from django.utils import timezone
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from administration.views import send_sms
from administration.forms import TicketForm
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from administration.models import Toilet, Problem, UserProfile
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


class ReportProblemAPI(APIView):
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
		except (Toilet.DoesNotExist, Toilet.MultipleObjectsReturned, Problem.DoesNotExist, Problem.MultipleObjectsReturned):
			return Response({'success': False, 'error': "Invalid Toilet/Problem"})
		tickets = []
		if not (problem_index=='1' and category_index=='5'):	
			tickets = Ticket.objects.filter(toilet=toilet,problem=problem).exclude(status=1)

		if not tickets:
	 		providers = Provider.objects.filter(toilets__toilet_id=toilet_id, problems__id=problem.category.id)
			if not providers:
				provider = None
			else:
				# TODO: Handle this better
				provider = providers[0]

	        # TODO: handle update ticket
			info_list = []
			info_list.append(phone_number)
			day = str(timezone.localtime(timezone.now()).date().day) if timezone.localtime(timezone.now()).date().day > 9 else '0'+str(timezone.localtime(timezone.now()).date().day)
			month = str(timezone.localtime(timezone.now()).date().month) if timezone.localtime(timezone.now()).date().month > 9 else '0'+str(timezone.localtime(timezone.now()).date().month) if timezone.localtime(timezone.now()).date().month > 9 else '0'+str(timezone.localtime(timezone.now()).date().month)
			year = str(timezone.localtime(timezone.now()).date().year)
			hours = str(timezone.localtime(timezone.now()).time().hour)
			minutes = str(timezone.localtime(timezone.now()).time().minute)
			time = ""
			if int(hours)>12:
				hours = str(int(hours)-12)
				if len(hours)==1:
					hours = '0'+hours
				if len(minutes)==1:
					minutes = '0'+minutes
				time = hours+":"+minutes+" PM"
			else:
				if len(hours)==1:
					hours = '0'+hours
				if len(minutes)==1:
					minutes = '0'+minutes
				time = hours+":"+minutes+" AM"
			info_list.append(day+"."+month+"."+year+" , "+time)
			comp_list = []
			comp_list.append(info_list)
			ticket = Ticket(phone_number=phone_number, toilet=toilet, problem=problem, provider=provider,additional_complaints_info=json.dumps(comp_list))
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
				ticket.is_audio_present = True
				ticket.save()

	        # send sms to the phone_number
			message = "Thank you for calling Mobile Sanitation to report the complaint. Your complaint has been registered with Ticket ID: " + str(ticket.id)
			send_sms(phone_number, message)

	        # send sms to the provider
			if provider:
				prob_desc = ticket.problem.description if ticket.problem.description!='others' else ticket.problem.category.description
				message = "A complaint of "+str(prob_desc)+" has been registered for Toilet ID: " + str(toilet_id) + ", Ticket ID: " + str(ticket.id)
				send_sms(provider.user_profile.phone_number, message)

			return Response({'success': True, 'ticket_id': ticket.id})
		else:
			ticket = tickets[0]
			ticket.complaints+=1
			info_list = []
			info_list.append(phone_number)
			day = str(timezone.localtime(timezone.now()).date().day) if timezone.localtime(timezone.now()).date().day > 9 else '0'+str(timezone.localtime(timezone.now()).date().day)
			month = str(timezone.localtime(timezone.now()).date().month) if timezone.localtime(timezone.now()).date().month > 9 else '0'+str(timezone.localtime(timezone.now()).date().month)
			year = str(timezone.localtime(timezone.now()).date().year)
			hours = str(timezone.localtime(timezone.now()).time().hour)
			minutes = str(timezone.localtime(timezone.now()).time().minute)
			time = ""
			if int(hours)>12:
				hours = str(int(hours)-12)
				if len(hours)==1:
					hours = '0'+hours
				if len(minutes)==1:
					minutes = '0'+minutes
				time = hours+":"+minutes+" PM"
			else:
				if len(hours)==1:
					hours = '0'+hours
				if len(minutes)==1:
					minutes = '0'+minutes
			info_list.append(day+"."+month+"."+year+" , "+time)
			jsonDec = json.decoder.JSONDecoder()
			complaint_list = jsonDec.decode(ticket.additional_complaints_info)
			complaint_list.append(info_list)
			ticket.additional_complaints_info = json.dumps(complaint_list)
			ticket.save()

			# send sms to the phone_number
			message = "Thank you for calling Mobile Sanitation to report the complaint. Your complaint has been registered with Ticket ID: " + str(ticket.id)
			send_sms(phone_number, message)

			# send sms to the provider
			if provider:
				prob_desc = ticket.problem.description if ticket.problem.description!='others' else ticket.problem.category.description
				message = "Another complaint of "+str(prob_desc)+" has been registered for Toilet ID: " + str(toilet_id) + ", Ticket ID: " + str(ticket.id)
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
        if download_response['success']:
            ticket.is_provider_audio_present = True
            ticket.save()
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


class ReportProblem(View):
    def get(self, request, ticket_id=None):
        user = UserProfile.objects.get(user=request.user)
        ticket = None
        if ticket_id:
            try:
                ticket = Ticket.objects.get(pk=ticket_id)
            except Ticket.DoesNotExist:
                return render(request, 'reporting/report_problem.html', {'user': user, 'error': 'Invalid Ticket ID'})
        ticket_form = TicketForm(instance=ticket)
        return render(request, 'reporting/report_problem.html', {'user': user, 'ticket_form': ticket_form})

    def post(self, request, ticket_id=None):
        phone_number = request.POST.get('phone_number')
        toilet_pk = request.POST.get('toilet')
        problem_pk = request.POST.get('problem')
        provider_pk = request.POST.get('provider')
        status = request.POST.get('status')
        provider_remarks = request.POST.get('provider_remarks')
        user_remarks = request.POST.get('user_remarks')
        manager_remarks = request.POST.get('manager_remarks')

        try:
            toilet = Toilet.objects.get(pk=toilet_pk)
            problem = Problem.objects.get(pk=problem_pk)
            if provider_pk:
                provider = Provider.objects.get(pk=provider_pk)
            else:
                provider = None
        except (Toilet.DoesNotExist, Problem.DoesNotExist, Provider.DoesNotExist):
            user = UserProfile.objects.get(user=request.user)
            ticket_form = TicketForm(data=request.POST)
            return render(request, 'reporting/report_problem.html', {'user': user, 'ticket_form': ticket_form,
                                                                     'error': "Invalid Input. Please enable "
                                                                              "JavaScript for validation."})

        if not provider:
            providers = Provider.objects.filter(toilets__toilet_id=toilet.toilet_id, problems__id=problem.category.id)
            if providers:
                # TODO: Handle this better
                provider = providers[0]

        # TODO: handle update ticket
        send_sms_to_reporter = True
        if not phone_number:
            send_sms_to_reporter = False
            phone_number = 'NIL'

        if ticket_id:
            try:
                ticket = Ticket.objects.get(pk=ticket_id)
            except Ticket.DoesNotExist:
                user = UserProfile.objects.get(user=request.user)
                ticket_form = TicketForm(data=request.POST)
                return render(request, 'reporting/report_problem.html', {'user': user, 'ticket_form': ticket_form,
                                                                         'error': "Invalid Ticket ID."})
            ticket.phone_number = phone_number
            ticket.toilet = toilet
            ticket.problem = problem
            ticket.provider = provider
            ticket.status = status
            ticket.provider_remarks = provider_remarks
            ticket.user_remarks = user_remarks
            ticket.manager_remarks = manager_remarks
            ticket.save()
        else:
            tickets = Ticket.objects.filter(toilet=toilet,problem=problem).exclude(status=1)
            if not tickets:
                info_list = []
                info_list.append(phone_number)
                day = str(timezone.localtime(timezone.now()).date().day) if timezone.localtime(timezone.now()).date().day > 9 else '0'+str(timezone.localtime(timezone.now()).date().day)
                month = str(timezone.localtime(timezone.now()).date().month) if timezone.localtime(timezone.now()).date().month > 9 else '0'+str(timezone.localtime(timezone.now()).date().month)
                year = str(timezone.localtime(timezone.now()).date().year)
                hours = str(timezone.localtime(timezone.now()).time().hour)
                minutes = str(timezone.localtime(timezone.now()).time().minute)
                time = ""
                if int(hours)>12:
                    hours = str(int(hours)-12)
                    if len(hours)==1:
                        hours = '0'+hours
                    if len(minutes)==1:
                        minutes = '0'+minutes
                    time = hours+":"+minutes+" PM"
                else:
                    if len(hours)==1:
                        hours = '0'+hours
                    if len(minutes)==1:
                        minutes = '0'+minutes
                    time = hours+":"+minutes+" AM"
                info_list.append(day+"."+month+"."+year+" , "+time)
                comp_list = []
                comp_list.append(info_list)
                ticket = Ticket(phone_number=phone_number, toilet=toilet, problem=problem, provider=provider,provider_remarks=provider_remarks, user_remarks=user_remarks,additional_complaints_info=json.dumps(comp_list))
                ticket.save()

                # send sms to the phone_number
                if send_sms_to_reporter:
                    message = "Thank you for calling Mobile Sanitation to report the complaint. Your complaint has been registered with Ticket ID: " + str(ticket.id)
                    send_sms(phone_number, message)

            # send sms to the provider
                if provider:
                    prob_desc = ticket.problem.description if ticket.problem.description!='others' else ticket.problem.category.description
                    message = "A Complaint of "+str(prob_desc)+" has registered for Toilet ID: " + str(toilet.toilet_id) + ", Ticket ID: " + str(
                        ticket.id) + ", Issue Reported: " + problem.category.description
                    if manager_remarks:
                        message += ", Manager remarks: " + manager_remarks
                    send_sms(provider.user_profile.phone_number, message)
            else:
            	ticket = tickets[0]
                ticket.complaints+=1
                info_list = []
                info_list.append(phone_number)
                day = str(timezone.localtime(timezone.now()).date().day) if timezone.localtime(timezone.now()).date().day > 9 else '0'+str(timezone.localtime(timezone.now()).date().day)
                month = str(timezone.localtime(timezone.now()).date().month) if timezone.localtime(timezone.now()).date().month > 9 else '0'+str(timezone.localtime(timezone.now()).date().month)
                year = str(timezone.localtime(timezone.now()).date().year)
                hours = str(timezone.localtime(timezone.now()).time().hour)
                minutes = str(timezone.localtime(timezone.now()).time().minute)
                time = ""
                
                if int(hours)>12:
                    hours = str(int(hours)-12)
                    if len(hours)==1:
                        hours = '0'+hours
                    if len(minutes)==1:
                        minutes = '0'+minutes
                    time = hours+":"+minutes+" PM"
                else:
                    if len(hours)==1:
                        hours = '0'+hours
                    if len(minutes)==1:
                        minutes = '0'+minutes
                    time = hours+":"+minutes+" AM"
                info_list.append(day+"."+month+"."+year+" , "+time)
                jsonDec = json.decoder.JSONDecoder()
                complaint_list = jsonDec.decode(ticket.additional_complaints_info)
                complaint_list.append(info_list)
                ticket.additional_complaints_info = json.dumps(complaint_list)
                ticket.provider_remarks += '\n'+provider_remarks
                ticket.user_remarks += '\n'+user_remarks
                ticket.manager_remarks += '\n'+manager_remarks
                ticket.save()

                # send sms to the phone_number
                if send_sms_to_reporter:
                    message = "Thank you for calling Mobile Sanitation to report the complaint. Your complaint has been registered with Ticket ID: " + str(ticket.id)
                    send_sms(phone_number, message)

            # send sms to the provider
                if provider:
                    prob_desc = ticket.problem.description if ticket.problem.description!='others' else ticket.problem.category.description
                    message = "Another Complaint of "+str(prob_desc)+" has registered for Toilet ID: " + str(toilet.toilet_id) + ", Ticket ID: " + str(
                        ticket.id) + ", Issue Reported: " + problem.category.description
                    if manager_remarks:
                        message += ", Manager remarks: " + manager_remarks
                    send_sms(provider.user_profile.phone_number, message)

        return HttpResponseRedirect(reverse('dashboard'))
