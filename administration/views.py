from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from django.db import transaction
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from administration.forms import UserProfileForm
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


"""
Begin: Views for managing managers
"""


class ViewManagers(View):
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        managers = Manager.objects.all()
        return render(request, 'administration/view_managers.html', {'user': user, 'managers': managers})


class AddManager(View):
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        user_profile_form = UserProfileForm()
        return render(request, 'administration/add_manager.html', {'user': user,
                                                                   'user_profile_form': user_profile_form})

    @transaction.atomic()
    def post(self, request):
        user = UserProfile.objects.get(user=request.user)
        user_profile_form = UserProfileForm()

        serializer = AddManagerSerializer(data=request.POST)
        if not serializer.is_valid():
            return render(request, 'administration/add_manager.html', {'user': user,
                                                                       'error': 'Please enable JavaScript',
                                                                       'user_profile_form': user_profile_form})
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
            picture = request.FILES['picture']
        else:
            picture = None

        try:
            User.objects.get(username=username)
            return render(request, 'administration/add_manager.html', {'user': user,
                                                                       'error': 'Username already exists!',
                                                                       'user_profile_form': user_profile_form})
        except User.DoesNotExist:
            pass
        try:
            User.objects.get(email=email)
            return render(request, 'administration/add_manager.html', {'user': user,
                                                                       'error': 'Email already exists!',
                                                                       'user_profile_form': user_profile_form})
        except User.DoesNotExist:
            pass

        manager_user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                                password=password, email=email)
        user_profile = UserProfile.objects.get(user=manager_user)
        user_profile.phone_number = phone_number
        user_profile.type = 'M'
        user_profile.address = address
        user_profile.picture = picture
        user_profile.save()

        manager = Manager(user_profile=user_profile)
        manager.save()

        return HttpResponseRedirect("/administration/view_manager/%d/" % manager.id)


class ViewManager(View):
    def get(self, request, manager_id):
        user = UserProfile.objects.get(user=request.user)
        manager = Manager.objects.get(pk=manager_id)
        return render(request, 'manager/dashboard.html', {'user': user, 'manager': manager})


class DeleteManager(View):
    def get(self, request, manager_id):
        try:
            Manager.objects.get(pk=manager_id).delete()
        except Manager.DoesNotExist:
            pass
        return HttpResponseRedirect(reverse('view_managers'))

"""
End: Views for managing managers
"""
