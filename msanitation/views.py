from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout

from administration.models import UserProfile, Toilet
from manager.models import Manager
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
            unresolved_tickets = len(filter(lambda ticket: ticket.status == Ticket.UNRESOLVED, tickets))
            resolved_tickets = total_tickets - unresolved_tickets

            return render(request, 'administration/dashboard.html', {'user': user, 'tickets': tickets,
                                                                     'total_tickets': total_tickets,
                                                                     'unresolved_tickets': unresolved_tickets,
                                                                     'resolved_tickets': resolved_tickets})
        elif user.type == 'M':
            manager = Manager.objects.get(user_profile=user)
            related_toilets = Toilet.objects.filter(providers__manager=manager)
            tickets = Ticket.objects.filter(toilet__in=related_toilets)

            total_tickets = len(tickets)
            unresolved_tickets = len(filter(lambda ticket: ticket.status == Ticket.UNRESOLVED, tickets))
            resolved_tickets = total_tickets - unresolved_tickets

            return render(request, 'manager/dashboard.html', {'user': user, 'manager': manager, 'tickets': tickets,
                                                              'total_tickets': total_tickets,
                                                              'unresolved_tickets': unresolved_tickets,
                                                              'resolved_tickets': resolved_tickets})
        elif user.type == 'P':
            tickets = Ticket.objects.filter(provider__user_profile=user)

            total_tickets = len(tickets)
            unresolved_tickets = len(filter(lambda ticket: ticket.status == Ticket.UNRESOLVED, tickets))
            resolved_tickets = total_tickets - unresolved_tickets

            return render(request, 'provider/dashboard.html', {'user': user, 'tickets': tickets,
                                                               'total_tickets': total_tickets,
                                                               'unresolved_tickets': unresolved_tickets,
                                                               'resolved_tickets': resolved_tickets})
        return HttpResponse("Invalid User")
