from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.contrib.auth.models import User

from administration.models import UserProfile, Toilet
from administration.forms import UserProfileForm
from manager.models import Manager
from provider.models import Provider
from reporting.models import Ticket




class Login(View):
    def get(self, request):
        if self.request.user and self.request.user.is_authenticated():
            return HttpResponseRedirect('/dashboard/')
        return render(request, 'login.html')

    def post(self, request):
        if self.request.user and self.request.user.is_authenticated():
            logout(request)

        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if not username or not password:
            return render(request, 'login.html', {'error': "Please enter username and password"})

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/dashboard/')
            else:
                return render(request, 'login.html', {'error': "User account disabled by administrator"})
        else:
            return render(request, 'login.html', {'error': "Invalid Login"})


class LogOut(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/login/')


class DashBoard(View):
    @method_decorator(login_required)
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        if user.type == 'A':
            tickets = Ticket.objects.all()
            total_tickets = len(tickets)

            unresolved_tickets = len(Ticket.objects.filter(status=0))
            resolved_tickets = len(Ticket.objects.filter(status=1))
            cannot_fix_tickets = len(Ticket.objects.filter(status=2))
            escalated_tickets = len(Ticket.objects.filter(status=3))

            return render(request, 'administration/dashboard.html', {'user': user, 'tickets': tickets,
                                                                     'total_tickets': total_tickets,
                                                                     'unresolved_tickets': unresolved_tickets,
                                                                     'resolved_tickets': resolved_tickets,
                                                                     'cannot_fix_tickets': cannot_fix_tickets,
                                                                     'escalated_tickets': escalated_tickets,})
        elif user.type == 'M':
            manager = Manager.objects.get(user_profile=user)
            related_toilets = Toilet.objects.filter(providers__manager=manager)
            tickets = Ticket.objects.filter(toilet__in=related_toilets)

            total_tickets = len(tickets)
            unresolved_tickets = len(Ticket.objects.filter(toilet__in=related_toilets,status=0))
            resolved_tickets = len(Ticket.objects.filter(toilet__in=related_toilets,status=1))
            cannot_fix_tickets = len(Ticket.objects.filter(toilet__in=related_toilets,status=2))
            escalated_tickets = len(Ticket.objects.filter(toilet__in=related_toilets,status=3))

            return render(request, 'manager/dashboard.html', {'user': user, 'manager': manager, 'tickets': tickets,
                                                              'total_tickets': total_tickets,
                                                              'unresolved_tickets': unresolved_tickets,
                                                              'resolved_tickets': resolved_tickets,
                                                              'cannot_fix_tickets': cannot_fix_tickets,
                                                              'escalated_tickets': escalated_tickets,})
        elif user.type == 'P':
            tickets = Ticket.objects.filter(provider__user_profile=user)
            total_tickets = len(tickets)
            unresolved_tickets = len(Ticket.objects.filter(toilet__in=related_toilets,status=0))
            resolved_tickets = len(Ticket.objects.filter(toilet__in=related_toilets,status=1))
            cannot_fix_tickets = len(Ticket.objects.filter(toilet__in=related_toilets,status=2))
            escalated_tickets = len(Ticket.objects.filter(toilet__in=related_toilets,status=3))

            return render(request, 'provider/dashboard.html', {'user': user, 'tickets': tickets,
                                                               'total_tickets': total_tickets,
                                                               'unresolved_tickets': unresolved_tickets,
                                                               'resolved_tickets': resolved_tickets,
                                                               'cannot_fix_tickets': cannot_fix_tickets,
                                                               'escalated_tickets': escalated_tickets,})
        return HttpResponse("Invalid User")


class Profile(View):
    @method_decorator(login_required)
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        user_profile_form = UserProfileForm(instance=user)
        if user.type == 'A':
            return render(request, 'administration/profile.html', {'user': user,
                                                                   'user_profile_form': user_profile_form})
        elif user.type == 'M':
            manager = Manager.objects.get(user_profile=user)
            return render(request, 'manager/profile.html', {'user': user, 'manager': manager,
                                                            'user_profile_form': user_profile_form})
        elif user.type == 'P':
            provider = Provider.objects.get(user_profile=user)
            return render(request, 'provider/profile.html', {'user': user, 'provider': provider,
                                                             'user_profile_form': user_profile_form})
        return HttpResponse("Invalid User")

    def post(self, request):
        user = UserProfile.objects.get(user=request.user)
        user_profile_form = UserProfileForm(instance=user)
        default_context = {'user': user, 'user_profile_form': user_profile_form}

        if user.type == 'A':
            profile_template = 'administration/profile.html'
        elif user.type == 'M':
            manager = Manager.objects.get(user_profile=user)
            default_context['manager'] = manager
            profile_template = 'manager/profile.html'
        elif user.type == 'P':
            provider = Provider.objects.get(user_profile=user)
            default_context['provider'] = provider
            profile_template = 'provider/profile.html'
        else:
            return HttpResponse("Invalid User")

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        picture = None
        if request.FILES:
            picture = request.FILES.get('picture')

        try:
            email_user = User.objects.get(email=email)
            if email_user != request.user:
                default_context['error'] = 'Email "' + email + '" already exists!'
                return render(request, profile_template, default_context)
        except User.DoesNotExist:
            pass

        user.user.first_name = first_name
        user.user.last_name = last_name
        if password:
            user.user.set_password(password)
        user.user.email = email
        user.user.save()

        user.phone_number = phone_number
        user.address = address
        if picture:
            user.picture = picture
        user.save()

        if user.type == 'M':
            pin_code = request.POST.get('pin_code')
            if pin_code:
                manager.pin_code = pin_code
                manager.save()
        elif user.type == 'P':
            pin_code = request.POST.get('pin_code')
            if pin_code:
                provider.pin_code = pin_code
                provider.save()

        return HttpResponseRedirect(reverse('dashboard'))


