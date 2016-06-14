import urllib2

from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from django.db import transaction
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from requests.utils import quote
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from administration.forms import UserProfileForm, ToiletForm
from administration.models import Admin, ProblemCategory, Problem, Toilet, UserProfile
from administration.serializers import AdminSerializer, ProblemCategorySerializer, ProblemSerializer, \
    ToiletSerializer, AddManagerSerializer, AddProviderSerializer
from manager.models import Manager
from provider.models import Provider
from provider.forms import ProviderForm
from reporting.models import Ticket


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


def send_sms(phone_number, message):
    api_key = "KK48377d55790faf6e93f66223c078ced3"
    params = "phone_no=" + phone_number + "&api_key=" + api_key + "&message=" + quote(message, safe='')
    url_root = "http://www.kookoo.in/outbound/outbound_sms.php?"
    url = url_root + params
    urllib2.urlopen(url).read()


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
        manager_id = serializer.validated_data['manager_id']
        pin_code = serializer.validated_data['pin_code']

        try:
            Manager.objects.get(manager_id=manager_id)
            return render(request, 'administration/add_manager.html', {'user': user,
                                                                       'error': 'Manager ID already exists!',
                                                                       'user_profile_form': user_profile_form})
        except Manager.DoesNotExist:
            pass

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

        Manager(user_profile=user_profile, manager_id=manager_id, pin_code=pin_code).save()

        return HttpResponseRedirect("/administration/view_manager/%s/" % manager_id)


class ViewManager(View):
    def get(self, request, manager_id):
        user = UserProfile.objects.get(user=request.user)
        manager = Manager.objects.get(manager_id=manager_id)
        related_toilets = Toilet.objects.filter(providers__manager=manager)
        tickets = Ticket.objects.filter(toilet__in=related_toilets)

        total_tickets = len(tickets)
        unresolved_tickets = len(filter(lambda ticket: ticket.status == Ticket.UNRESOLVED, tickets))
        resolved_tickets = total_tickets - unresolved_tickets

        return render(request, 'manager/dashboard.html', {'user': user, 'manager': manager, 'tickets': tickets,
                                                          'total_tickets': total_tickets,
                                                          'unresolved_tickets': unresolved_tickets,
                                                          'resolved_tickets': resolved_tickets})


class EditManager(View):
    def get(self, request, manager_id):
        user = UserProfile.objects.get(user=request.user)
        manager = get_object_or_404(Manager, manager_id=manager_id)
        user_profile_form = UserProfileForm(instance=manager.user_profile)
        return render(request, 'administration/add_manager.html', {'user': user,
                                                                   'user_profile_form': user_profile_form,
                                                                   'first_name': manager.user_profile.user.first_name,
                                                                   'last_name': manager.user_profile.user.last_name,
                                                                   'username': manager.user_profile.user.username,
                                                                   'manager_id': manager.manager_id,
                                                                   'pin_code': manager.pin_code,
                                                                   'email': manager.user_profile.user.email,
                                                                   'picture': manager.user_profile.picture})

    @transaction.atomic()
    def post(self, request, manager_id):
        user = UserProfile.objects.get(user=request.user)
        manager = get_object_or_404(Manager, manager_id=manager_id)
        user_profile_form = UserProfileForm(instance=manager.user_profile)

        default_context = {'user': user,
                           'error': 'Please enable JavaScript',
                           'user_profile_form': user_profile_form}

        default_context['first_name'] = request.POST.get('first_name')
        default_context['last_name'] = request.POST.get('last_name')
        default_context['username'] = request.POST.get('username')
        default_context['password'] = request.POST.get('password')
        default_context['manager_id'] = manager_id
        default_context['pin_code'] = request.POST.get('pin_code')
        default_context['email'] = request.POST.get('email')
        default_context['phone_number'] = request.POST.get('phone_number')
        default_context['address'] = request.POST.get('address')
        default_context['picture'] = request.FILES.get('picture')

        serializer = AddManagerSerializer(data=request.POST)
        if not serializer.is_valid():
            return render(request, 'administration/add_manager.html', default_context)

        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        password = serializer.validated_data['password']
        pin_code = serializer.validated_data['pin_code']
        email = serializer.validated_data['email']
        if not email:
            email = serializer.validated_data['username'] + "@example.com"
        phone_number = serializer.validated_data['phone_number']
        address = serializer.validated_data['address']
        if request.FILES:
            picture = request.FILES['picture']
        else:
            picture = None

        try:
            email_user = User.objects.get(email=email)
            if email_user != manager.user_profile.user:
                default_context['error'] = 'Email already exists!'
                return render(request, 'administration/add_manager.html', default_context)
        except User.DoesNotExist:
            pass

        user_profile = manager.user_profile
        user = user_profile.user

        user.first_name = first_name
        user.last_name = last_name
        if password:
            user.set_password(password)
        user.email = email
        user.save()

        user_profile.phone_number = phone_number
        user_profile.address = address
        if picture:
            user_profile.picture = picture
        user_profile.save()

        manager.pin_code = pin_code
        manager.save()

        return HttpResponseRedirect("/administration/view_manager/%s/" % manager.manager_id)


class DeleteManager(View):
    def get(self, request, manager_id):
        try:
            Manager.objects.get(manager_id=manager_id).delete()
        except Manager.DoesNotExist:
            pass
        return HttpResponseRedirect(reverse('view_managers'))


"""
End: Views for managing managers
"""

"""
Begin: Views for managing providers
"""


class ViewProviders(View):
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        providers = Provider.objects.all()
        return render(request, 'administration/view_providers.html', {'user': user, 'providers': providers})


class AddProvider(View):
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        user_profile_form = UserProfileForm()
        provider_form = ProviderForm()
        return render(request, 'administration/add_provider.html', {'user': user,
                                                                    'user_profile_form': user_profile_form,
                                                                    'provider_form': provider_form})

    @transaction.atomic()
    def post(self, request):
        user = UserProfile.objects.get(user=request.user)
        user_profile_form = UserProfileForm()
        provider_form = ProviderForm()

        serializer = AddProviderSerializer(data=request.POST)
        if not serializer.is_valid():
            return render(request, 'administration/add_provider.html', {'user': user,
                                                                        'error': 'Please enable JavaScript',
                                                                        'user_profile_form': user_profile_form,
                                                                        'provider_form': provider_form})
        provider_id = serializer.validated_data['provider_id']
        try:
            Provider.objects.get(provider_id=provider_id)
            return render(request, 'administration/add_provider.html', {'user': user,
                                                                        'error': 'Provider ID already exists!',
                                                                        'user_profile_form': user_profile_form,
                                                                        'provider_form': provider_form})
        except Provider.DoesNotExist:
            pass

        # Create User
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        if not password:
            password = '123456'
        email = serializer.validated_data['email']
        if not email:
            email = username + "@example.com"
        try:
            User.objects.get(username=username)
            return render(request, 'administration/add_provider.html', {'user': user,
                                                                        'error': 'Username already exists!',
                                                                        'user_profile_form': user_profile_form,
                                                                        'provider_form': provider_form})
        except User.DoesNotExist:
            pass
        try:
            User.objects.get(email=email)
            return render(request, 'administration/add_provider.html', {'user': user,
                                                                        'error': 'Email already exists!',
                                                                        'user_profile_form': user_profile_form,
                                                                        'provider_form': provider_form})
        except User.DoesNotExist:
            pass

        provider_user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                                 password=password, email=email)

        # Create the user_profile
        phone_number = serializer.validated_data['phone_number']
        address = serializer.validated_data['address']
        picture = None
        if request.FILES:
            picture = request.FILES['picture']

        user_profile = UserProfile.objects.get(user=provider_user)
        user_profile.phone_number = phone_number
        user_profile.address = address
        user_profile.picture = picture
        user_profile.type = 'P'
        user_profile.save()

        # Create the provider
        manager = serializer.validated_data['manager']
        # provider_id = serializer.validated_data['provider_id']
        pin_code = serializer.validated_data['pin_code']
        toilets = serializer.validated_data['toilets']
        problems = serializer.validated_data['problems']

        provider = Provider(user_profile=user_profile, provider_id=provider_id, pin_code=pin_code, manager=manager)
        provider.save()
        provider.toilets.add(*toilets)
        provider.problems.add(*problems)

        return HttpResponseRedirect("/administration/view_provider/%s/" % provider.provider_id)


class ViewProvider(View):
    def get(self, request, provider_id):
        user = UserProfile.objects.get(user=request.user)
        provider = Provider.objects.get(provider_id=provider_id)
        tickets = Ticket.objects.filter(provider=provider)

        total_tickets = len(tickets)
        unresolved_tickets = len(filter(lambda ticket: ticket.status == Ticket.UNRESOLVED, tickets))
        resolved_tickets = total_tickets - unresolved_tickets

        return render(request, 'provider/dashboard.html', {'user': user, 'provider': provider, 'tickets': tickets,
                                                           'total_tickets': total_tickets,
                                                           'unresolved_tickets': unresolved_tickets,
                                                           'resolved_tickets': resolved_tickets})


class DeleteProvider(View):
    def get(self, request, provider_id):
        try:
            Provider.objects.get(provider_id=provider_id).delete()
        except Provider.DoesNotExist:
            pass
        return HttpResponseRedirect(reverse('view_providers'))


"""
End: Views for managing providers
"""

"""
Begin: Views for managing toilets
"""


class ViewToilets(View):
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        toilets = Toilet.objects.all()
        return render(request, 'administration/view_toilets.html', {'user': user, 'toilets': toilets})


class AddToilet(View):
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        toilet_form = ToiletForm()
        return render(request, 'administration/add_toilet.html', {'user': user,
                                                                  'toilet_form': toilet_form})

    @transaction.atomic()
    def post(self, request):
        user = UserProfile.objects.get(user=request.user)

        address = request.POST.get('address')
        toilet_id = request.POST.get('toilet_id')

        if not address or not toilet_id:
            toilet_form = ToiletForm()
            return render(request, 'administration/add_toilet.html', {'user': user,
                                                                      'error': 'Please enable javascript!',
                                                                      'toilet_form': toilet_form})
        try:
            Toilet.objects.get(toilet_id=toilet_id)
            toilet_form = ToiletForm(data=request.POST)
            return render(request, 'administration/add_toilet.html', {'user': user,
                                                                      'error': 'Toilet ID already exists!',
                                                                      'toilet_form': toilet_form})
        except Toilet.DoesNotExist:
            pass

        # Create Toilet
        toilet = Toilet(toilet_id=toilet_id, address=address)
        toilet.save()

        return HttpResponseRedirect("/administration/view_toilets/")


class DeleteToilet(View):
    def get(self, request, toilet_id):
        try:
            Toilet.objects.get(toilet_id=toilet_id).delete()
        except Toilet.DoesNotExist:
            pass
        return HttpResponseRedirect(reverse('view_toilets'))


"""
End: Views for managing toilets
"""
