from rest_framework import viewsets
from django.views.generic import View
from django.shortcuts import render

from manager.models import Manager
from manager.serializers import ManagerSerializer
from administration.models import UserProfile


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer


class ViewManagers(View):
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        return render(request, 'manager/view.html', {'user': user})


class AddManager(View):
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        return render(request, 'manager/add.html', {'user': user})

    def post(self, request):
        user = UserProfile.objects.get(user=request.user)
        print request.POST
        return render(request, 'manager/add.html', {'user': user})
