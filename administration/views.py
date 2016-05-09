from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from django.db import transaction
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from administration.forms import ToiletForm, UserForm, TicketForm, ProblemForm
from administration.models import Admin, ProblemCategory, Problem, Toilet, UserProfile
from administration.serializers import AdminSerializer, ProblemCategorySerializer, ProblemSerializer, \
    ToiletSerializer, AddManagerSerializer
from manager.models import Manager


class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer


class ProblemCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProblemCategory.objects.all()
    serializer_class = ProblemCategorySerializer

    @detail_route(methods=['GET'])
    def problems(self, request, pk=None):
        problem_category = get_object_or_404(ProblemCategory, pk=pk)
        serializer = ProblemSerializer(problem_category.problems.all(), many=True)
        return Response(serializer.data)


class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer


class ToiletViewSet(viewsets.ModelViewSet):
    queryset = Toilet.objects.all()
    serializer_class = ToiletSerializer


class TicketView(View):
    def get(self, request):
        ticket_form = TicketForm()
        return render(request, 'administration/tickets.html', {'ticket_form': ticket_form, 'active': 'ticket'})

    def post(self, request):
        return Response({'success': True})


class UserView(View):
    def get(self, request):
        user_form = UserForm()
        return render(request, 'administration/base.html', {'user_form': user_form, 'active': 'user'})

    def post(self, request):
        return Response({'success': True})


class ToiletView(View):
    def get(self, request):
        toilet_form = ToiletForm()
        return render(request, 'administration/toilets.html', {'toilet_form': toilet_form, 'active': 'toilet'})

    def post(self, request):
        return Response({'success': True})


class ProblemView(View):
    def get(self, request):
        problem_form = ProblemForm()
        return render(request, 'administration/problems.html', {'problem_form': problem_form, 'active': 'problem'})

    def post(self, request):
        return Response({'success': True})


class ViewManagers(View):
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        managers = Manager.objects.all()
        return render(request, 'administration/view_managers.html', {'user': user, 'managers': managers})


class AddManager(View):
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        return render(request, 'administration/add_manager.html', {'user': user})

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
