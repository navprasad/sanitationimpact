from django.views.generic import View
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login


class Login(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
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
