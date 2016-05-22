from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
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


class IsValidManager(APIView):
    def post(self, request):
        manager_id = request.data.get('manager_id', None)
        if not manager_id:
            return Response({'success': False, 'error': "Invalid POST data"})
        try:
            Manager.objects.get(pk=manager_id)
        except (Manager.DoesNotExist, Manager.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Manager ID"})
        return Response({'success': True})


class IsValidManagerPinCode(APIView):
    def post(self, request):
        manager_id = request.data.get('manager_id', None)
        pin_code = request.data.get('pin_code', None)
        if not manager_id or not pin_code:
            return Response({'success': False, 'error': "Invalid POST data"})
        try:
            Manager.objects.get(pk=manager_id, pin_code=pin_code)
        except (Manager.DoesNotExist, Manager.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Manager ID/PIN Code"})
        return Response({'success': True})
