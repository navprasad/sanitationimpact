from rest_framework import viewsets
from django.db import transaction
from django.views.generic import View
from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.models import User

from manager.models import Manager
from manager.serializers import ManagerSerializer, AddManagerSerializer
from administration.models import UserProfile


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer


class ViewManagers(View):
    def get(self, request):
        managers = Manager.objects.all()
        return render(request, 'manager/view.html', {'managers': managers})


class AddManager(View):
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        return render(request, 'manager/add.html', {'user': user})

    @transaction.atomic()
    def post(self, request):
        user = UserProfile.objects.get(user=request.user)
        serializer = AddManagerSerializer(data=request.POST)
        if not serializer.is_valid():
            return render(request, 'manager/add.html', {'user': user, 'error': 'Enable JavaScript'})
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        if not password:
            password = '123456'
        email = serializer.validated_data['email']
        if not email:
            email = username + "@example.com"
        phone_number = serializer.validated_data['phone_number']
        address = serializer.validated_data['address']

        if request.FILES:
            profile_picture = request.FILES['profile_picture']
        else:
            profile_picture = None

        user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                        password=password, email=email)
        user_profile = UserProfile(user=user, phone_number=phone_number, type='M', address=address, picture=profile_picture)
        user_profile.save()
        manager = Manager(user_profile=user_profile)
        manager.save()

        return HttpResponseRedirect("/manager/%d/" % manager.id)


class ManagerProfile(View):
    def get(self, request, pk):
        manager = Manager.objects.get(pk=pk)
        return render(request, 'administration/profile.html', {'user': manager})

