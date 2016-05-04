from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout

from administration.models import UserProfile


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
            return render(request, 'administration/dashboard.html', {'user': user})
        elif user.type == 'M':
            return render(request, 'manager/dashboard.html')
        elif user.type == 'P':
            return render(request, 'provider/dashboard.html')
        return HttpResponse("Invalid User")
