from rest_framework import viewsets
from django.views.generic import View
from django.shortcuts import render

from manager.models import Manager
from manager.serializers import ManagerSerializer


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer


class ManagerProfile(View):
    def get(self, request, pk):
        manager = Manager.objects.get(pk=pk)
        return render(request, 'administration/profile.html', {'user': manager})

