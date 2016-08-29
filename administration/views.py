import urllib2
import json
import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from django.db import transaction
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
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
from manager.forms import ManagerForm
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
    phone_number = str(phone_number)
    quote_message = quote(message, safe='')
    url = "http://smscloud.ozonetel.com/GatewayAPI/rest?send_to=" + phone_number + "&msg=" + quote_message + "&msg_type=text&loginid=sis_foundation&auth_scheme=plain&password=cisokQeUr&v=1.1&format=text&method=sendMessage&mask=TOILEQ"
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
        manager_form = ManagerForm()
        return render(request, 'administration/add_manager.html', {'user': user,
                                                                   'manager_form': manager_form,
                                                                   'user_profile_form': user_profile_form})

    @transaction.atomic()
    def post(self, request):
        user = UserProfile.objects.get(user=request.user)
        manager_form = ManagerForm()
        user_profile_form = UserProfileForm()

        serializer = AddManagerSerializer(data=request.POST)
        if not serializer.is_valid():
            return render(request, 'administration/add_manager.html', {'user': user,
                                                                       'error': 'Please enable JavaScript',
                                                                       'manager_form': manager_form,
                                                                       'user_profile_form': user_profile_form})
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        manager_id = serializer.validated_data['manager_id']
        pin_code = serializer.validated_data['pin_code']
        description = serializer.validated_data['description']

        try:
            Manager.objects.get(manager_id=manager_id)
            return render(request, 'administration/add_manager.html', {'user': user,
                                                                       'error': 'Manager ID already exists!',
                                                                       'manager_form': manager_form,
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
        manager_code = serializer.validated_data['manager_code']

        if request.FILES:
            picture = request.FILES['picture']
        else:
            picture = None

        try:
            User.objects.get(username=username)
            return render(request, 'administration/add_manager.html', {'user': user,
                                                                       'error': 'Username already exists!',
                                                                       'manager_form': manager_form,
                                                                       'user_profile_form': user_profile_form})
        except User.DoesNotExist:
            pass
        try:
            User.objects.get(email=email)
            return render(request, 'administration/add_manager.html', {'user': user,
                                                                       'error': 'Email already exists!',
                                                                       'manager_form': manager_form,
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

        Manager(user_profile=user_profile, manager_id=manager_id, pin_code=pin_code, description=description,
                manager_code=manager_code).save()

        return HttpResponseRedirect("/administration/view_manager/%s/" % manager_id)


class ViewManager(View):
    def get(self, request, manager_id):
        user = UserProfile.objects.get(user=request.user)
        manager = Manager.objects.get(manager_id=manager_id)
        related_toilets = Toilet.objects.filter(providers__manager=manager)
        tickets = Ticket.objects.filter(toilet__in=related_toilets)
        total_tickets = len(tickets)
        unresolved_tickets = len(Ticket.objects.filter(status=0,toilet__in=related_toilets))
        resolved_tickets = len(Ticket.objects.filter(status=1,toilet__in=related_toilets))
        cannot_fix_tickets = len(Ticket.objects.filter(status=2,toilet__in=related_toilets))
        escalated_tickets = len(Ticket.objects.filter(status=3,toilet__in=related_toilets))

        return render(request, 'manager/dashboard.html', {'user': user, 'manager': manager, 'tickets': tickets,
                                                          'total_tickets': total_tickets,
                                                          'unresolved_tickets': unresolved_tickets,
                                                          'resolved_tickets': resolved_tickets,
                                                          'cannot_fix_tickets': cannot_fix_tickets,
                                                          'escalated_tickets': escalated_tickets,})


class EditManager(View):
    def get(self, request, manager_id):
        user = UserProfile.objects.get(user=request.user)
        manager = get_object_or_404(Manager, manager_id=manager_id)
        user_profile_form = UserProfileForm(instance=manager.user_profile)
        manager_form = ManagerForm(instance=manager)
        return render(request, 'administration/add_manager.html', {'user': user,
                                                                   'user_profile_form': user_profile_form,
                                                                   'manager_form': manager_form,
                                                                   'first_name': manager.user_profile.user.first_name,
                                                                   'last_name': manager.user_profile.user.last_name,
                                                                   'username': manager.user_profile.user.username,
                                                                   'manager_id': manager.manager_id,
                                                                   'pin_code': manager.pin_code,
                                                                   'description': manager.description,
                                                                   'email': manager.user_profile.user.email,
                                                                   'picture': manager.user_profile.picture})

    @transaction.atomic()
    def post(self, request, manager_id):
        user = UserProfile.objects.get(user=request.user)
        manager = get_object_or_404(Manager, manager_id=manager_id)
        user_profile_form = UserProfileForm(instance=manager.user_profile)
        manager_form = ManagerForm(instance=manager)

        default_context = {'user': user,
                           'error': 'Please enable JavaScript',
                           'manager_form': manager_form,
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
        default_context['description'] = request.POST.get('description')
        default_context['picture'] = request.FILES.get('picture')

        serializer = AddManagerSerializer(data=request.POST)
        if not serializer.is_valid():
            return render(request, 'administration/add_manager.html', default_context)

        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        password = serializer.validated_data['password']
        pin_code = serializer.validated_data['pin_code']
        description = serializer.validated_data['description']
        email = serializer.validated_data['email']
        if not email:
            email = serializer.validated_data['username'] + "@example.com"
        phone_number = serializer.validated_data['phone_number']
        address = serializer.validated_data['address']
        manager_code = serializer.validated_data['manager_code']
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
        manager.description = description
        manager.manager_code = manager_code
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
        description = serializer.validated_data['description']
        provider_code = serializer.validated_data['provider_code']

        provider = Provider(user_profile=user_profile, provider_id=provider_id, pin_code=pin_code, manager=manager,
                            description=description, provider_code=provider_code)
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
        unresolved_tickets = len(Ticket.objects.filter(status=0,provider=provider))
        resolved_tickets = len(Ticket.objects.filter(status=1,provider=provider))
        cannot_fix_tickets = len(Ticket.objects.filter(status=2,provider=provider))
        escalated_tickets = len(Ticket.objects.filter(status=3,provider=provider))

        return render(request, 'provider/dashboard.html', {'user': user, 'provider': provider, 'tickets': tickets,
                                                           'total_tickets': total_tickets,
                                                           'unresolved_tickets': unresolved_tickets,
                                                           'resolved_tickets': resolved_tickets,
                                                           'cannot_fix_tickets': cannot_fix_tickets,
                                                           'escalated_tickets': escalated_tickets})


class EditProvider(View):
    def get(self, request, provider_id):
        user = UserProfile.objects.get(user=request.user)
        provider = get_object_or_404(Provider, provider_id=provider_id)
        user_profile_form = UserProfileForm(instance=provider.user_profile)
        provider_form = ProviderForm(instance=provider)
        return render(request, 'administration/add_provider.html', {'user': user,
                                                                    'user_profile_form': user_profile_form,
                                                                    'provider_form': provider_form,
                                                                    'first_name': provider.user_profile.user.first_name,
                                                                    'last_name': provider.user_profile.user.last_name,
                                                                    'username': provider.user_profile.user.username,
                                                                    'provider_id': provider.provider_id,
                                                                    'pin_code': provider.pin_code,
                                                                    'email': provider.user_profile.user.email,
                                                                    'picture': provider.user_profile.picture})

    @transaction.atomic()
    def post(self, request, provider_id):
        """

        """
        user = UserProfile.objects.get(user=request.user)
        provider = get_object_or_404(Provider, provider_id=provider_id)
        user_profile_form = UserProfileForm(instance=provider.user_profile)
        provider_form = ProviderForm(instance=provider)

        default_context = {'user': user,
                           'error': 'Please enable JavaScript',
                           'user_profile_form': user_profile_form,
                           'provider_form': provider_form}

        default_context['first_name'] = request.POST.get('first_name')
        default_context['last_name'] = request.POST.get('last_name')
        default_context['username'] = request.POST.get('username')
        default_context['password'] = request.POST.get('password')
        default_context['provider_id'] = provider_id
        default_context['pin_code'] = request.POST.get('pin_code')
        default_context['email'] = request.POST.get('email')
        default_context['phone_number'] = request.POST.get('phone_number')
        default_context['manager_id'] = request.POST.get('manager')
        default_context['toilets'] = request.POST.getlist('toilets')
        default_context['problems'] = request.POST.getlist('problems')
        default_context['address'] = request.POST.get('address')
        default_context['description'] = request.POST.get('description')
        default_context['provider_code'] = request.POST.get('provider_code')
        default_context['picture'] = request.FILES.get('picture')

        serializer = AddProviderSerializer(data=request.POST)
        if not serializer.is_valid():
            return render(request, 'administration/add_provider.html', default_context)

        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        password = serializer.validated_data['password']
        email = serializer.validated_data['email']
        if not email:
            email = serializer.validated_data['username'] + "@example.com"
        pin_code = serializer.validated_data['pin_code']
        manager = serializer.validated_data['manager']
        phone_number = serializer.validated_data['phone_number']
        address = serializer.validated_data['address']
        description = serializer.validated_data['description']
        provider_code = serializer.validated_data['provider_code']
        picture = None
        if request.FILES:
            picture = request.FILES['picture']
        toilets = serializer.validated_data['toilets']
        problems = serializer.validated_data['problems']

        try:
            email_user = User.objects.get(email=email)
            if email_user != provider.user_profile.user:
                default_context['error'] = 'Email already exists!'
                return render(request, 'administration/add_provider.html', default_context)
        except User.DoesNotExist:
            pass

        user_profile = provider.user_profile
        user = user_profile.user

        # save user details
        user.first_name = first_name
        user.last_name = last_name
        if password:
            user.set_password(password)
        user.email = email
        user.save()

        # save user_profile details
        user_profile.phone_number = phone_number
        user_profile.address = address
        if picture:
            user_profile.picture = picture
        user_profile.save()

        # save provider details
        provider.pin_code = pin_code
        provider.manager = manager
        provider.description = description
        provider.toilets.clear()
        provider.toilets.add(*toilets)
        provider.problems.clear()
        provider.problems.add(*problems)
        provider.provider_code = provider_code
        provider.save()

        return HttpResponseRedirect("/administration/view_provider/%s/" % provider.provider_id)


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
        sex = request.POST.get('sex')
        payment = request.POST.get('payment')
        type = request.POST.get('type')
        location_code = request.POST.get('location_code')
        area = request.POST.get('area')

        if not address or not toilet_id:
            toilet_form = ToiletForm(data=request.POST)
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

        if not sex:
            sex = 'B'
        if not payment:
            payment = 'F'
        if not type:
            type = 'P'
        if not area:
            area = 'R'
        if not location_code:
            location_code = ''

        # Create Toilet
        toilet = Toilet(toilet_id=toilet_id, address=address, sex=sex, payment=payment, type=type,
                        location_code=location_code, area=area)
        toilet.save()

        return HttpResponseRedirect("/administration/view_toilets/")


class EditToilet(View):
    def get(self, request, toilet_id):
        user = UserProfile.objects.get(user=request.user)
        toilet = get_object_or_404(Toilet, toilet_id=toilet_id)
        toilet_form = ToiletForm(instance=toilet)
        return render(request, 'administration/add_toilet.html', {'user': user,
                                                                  'toilet_form': toilet_form})

    @transaction.atomic()
    def post(self, request, toilet_id):
        user = UserProfile.objects.get(user=request.user)
        toilet = get_object_or_404(Toilet, toilet_id=toilet_id)

        address = request.POST.get('address')
        toilet_id = request.POST.get('toilet_id')
        sex = request.POST.get('sex')
        payment = request.POST.get('payment')
        type = request.POST.get('type')
        area = request.POST.get('area')
        location_code = request.POST.get('location_code')

        if not address or not toilet_id:
            toilet_form = ToiletForm(data=request.POST)
            return render(request, 'administration/add_toilet.html', {'user': user,
                                                                      'error': 'Please enable javascript!',
                                                                      'toilet_form': toilet_form})
        try:
            test_toilet = Toilet.objects.get(toilet_id=toilet_id)
            if test_toilet != toilet:
                toilet_form = ToiletForm(data=request.POST)
                return render(request, 'administration/add_toilet.html', {'user': user,
                                                                          'error': 'Toilet ID already exists!',
                                                                          'toilet_form': toilet_form})
        except Toilet.DoesNotExist:
            pass

        if not sex:
            sex = 'B'
        if not payment:
            payment = 'F'
        if not type:
            type = 'P'
        if not area:
            area = 'R'
        if not location_code:
            location_code = ''

        # Edit Toilet
        toilet.toilet_id = toilet_id
        toilet.address = address
        toilet.sex = sex
        toilet.payment = payment
        toilet.type = type
        toilet.location_code = location_code
        toilet.area = area
        toilet.save()

        return HttpResponseRedirect("/administration/view_toilets/")


class DeleteToilet(View):
    def get(self, request, toilet_id):
        try:
            Toilet.objects.get(toilet_id=toilet_id).delete()
        except Toilet.DoesNotExist:
            pass
        return HttpResponseRedirect(reverse('view_toilets'))

class ShowComplaints(View):
    def get(self,request,ticket_id):
        user = UserProfile.objects.get(user=request.user)
        ticket = get_object_or_404(Ticket,id=ticket_id)
        jsonDec = json.decoder.JSONDecoder()
        complaint_list = jsonDec.decode(ticket.additional_complaints_info)
        return render(request, 'administration/complaints.html', {'complaints': complaint_list,'user':user})

class DisplayStats(View):
    def get(self, request):
        user = UserProfile.objects.get(user=request.user)
        problem_category = ProblemCategory.objects.all()
        providers = Provider.objects.all()
        managers = Manager.objects.all()
        toilets = Toilet.objects.all()
        toilet_locations = set()
        toilet_areas = (
        ('R', 'Rural'),
        ('U', 'Urban'),
        ('PU', 'Peri Urban')
    )
        toilet_types = (
        ('C', 'Community'),
        ('P', 'Public'),
        ('S', 'School'),
        ('W', 'Women Sanitation Complex')
    )
        toilet_gender = (
        ('B', 'Both'),
        ('M', 'Male'),
        ('F', 'Female')
    )
        toilet_payments =(
        ('P', 'Paid'),
        ('F', 'Free'),
        ('B', 'Both (Pay + No Pay)'),
        ('H', 'Household Contribution')
    )
        for toilet in toilets:
            toilet_locations.add(toilet.location_code)
        toilet_locations = sorted(list(toilet_locations))
        stats = []
        total = 0
        for pc in problem_category:
            l=[]
            today = timezone.localtime(timezone.now())
            tickets = Ticket.objects.filter(problem__category=pc,timestamp__month=today.month)
            sum=0
            for ticket in tickets:
                sum+=ticket.complaints
            if pc.description!='others':
                l.append(pc.description)
                l.append(sum)
                total+=sum
                stats.append(l)
        percentages = []
        for stat in stats:
            if total!=0:
                percentages.append(round(100 * float(stat[1])/float(total),2))
            else:
                percentages.append(0)
        stats = zip(stats,percentages)
        title = 'for '+today.strftime("%B")
        return render(request, 'administration/stats.html', {'user':user,'title':title,'toilets':toilets,'toilet_locations':toilet_locations,'toilet_areas':toilet_areas,'toilet_types':toilet_types,'toilet_gender':toilet_gender,'toilet_payments':toilet_payments,'providers':providers,'managers':managers,'problem_category':problem_category,'stats':stats,})

    def post(self,request):
        user = UserProfile.objects.get(user=request.user)
        problem_category = ProblemCategory.objects.all()
        providers = Provider.objects.all()
        managers = Manager.objects.all()
        toilets = Toilet.objects.all()
        toilet_locations = set()
        toilet_areas = (
        ('R', 'Rural'),
        ('U', 'Urban'),
        ('PU', 'Peri Urban')
    )
        toilet_types = (
        ('C', 'Community'),
        ('P', 'Public'),
        ('S', 'School'),
        ('W', 'Women Sanitation Complex')
    )
        toilet_gender = (
        ('B', 'Both'),
        ('M', 'Male'),
        ('F', 'Female')
    )
        toilet_payments =(
        ('P', 'Paid'),
        ('F', 'Free'),
        ('B', 'Both (Pay + No Pay)'),
        ('H', 'Household Contribution')
    )
        status = request.POST.get('status_category')
        if status=='All':
            status = [0,1,2,3]
        else:
            status = [status]
        for toilet in toilets:
            toilet_locations.add(toilet.location_code)
        toilet_locations = list(sorted(toilet_locations))
        selected_problem_category = request.POST.get('problem_category')
        startdate = request.POST.get('startDate')
        temp = startdate.split('/')
        if len(temp)==3:
            startdate = datetime.date(int(temp[2]), int(temp[0]), int(temp[1]))
        enddate = request.POST.get('endDate')
        temp = enddate.split('/')
        if len(temp)==3:
            enddate = datetime.date(int(temp[2]), int(temp[0]), int(temp[1]))
            enddate = enddate + datetime.timedelta(days=1)
        title=''
        total=0
        if selected_problem_category=='All Categories':
            filter_category = request.POST.get('filter_category')

            if filter_category == 'All':
                stats = []
                for pc in problem_category:
                    l=[]
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem__category=pc,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                        total+=sum
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)
                stats = zip(stats,percentages)
            
            if filter_category == 'Filter By Provider':
                stats = []
                for pc in problem_category:
                    l=[]
                    provider_id = request.POST.get('providerSelect')
                    provider = Provider.objects.get(id=provider_id)
                    title = '(Provider:'+provider.user_profile.user.first_name+' '+provider.user_profile.user.last_name+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,provider=provider,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,provider=provider,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,provider=provider,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem__category=pc,provider=provider,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total+=sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)  
                stats = zip(stats,percentages)
            if filter_category == 'Filter By Manager':
                stats = []
                for pc in problem_category:
                    l=[]
                    manager_id = request.POST.get('managerSelect')
                    manager = Manager.objects.get(id=manager_id)
                    title = '(Manager:'+manager.user_profile.user.first_name+' '+manager.user_profile.user.last_name+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,provider__manager=manager,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,provider__manager=manager,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,provider__manager=manager,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem__category=pc,provider__manager=manager,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total+=sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)  
                stats = zip(stats,percentages)
            if filter_category == 'Filter By Toilet ID':
                stats = []
                for pc in problem_category:
                    l=[]
                    toilet_id = request.POST.get('toiletSelect')
                    toilet = Toilet.objects.get(id=toilet_id)
                    title = '(Toilet ID:'+toilet.toilet_id+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet=toilet,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet=toilet,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet=toilet,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem__category=pc,toilet=toilet,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total+=sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)  
                stats = zip(stats,percentages) 
            if filter_category == 'Filter By Toilet Location Code':
                stats = []
                for pc in problem_category:
                    l=[]
                    location_code= request.POST.get('toiletLocationSelect')
                    title = '(Toilet Location Code:'+location_code+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__location_code=location_code,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__location_code=location_code,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__location_code=location_code,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__location_code=location_code,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total+=sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)  
                stats = zip(stats,percentages) 
            if filter_category == 'Filter By Toilet Area':
                stats = []
                for pc in problem_category:
                    l=[]
                    area= request.POST.get('toiletAreaSelect')
                    for toilet_area in toilet_areas:
                        if toilet_area[0]==area:
                            title = '(Toilet Area:'+toilet_area[1]+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__area=area,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__area=area,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__area=area,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__area=area,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total+=sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)  
                stats = zip(stats,percentages) 
            if filter_category == 'Filter By Toilet Type':
                stats = []
                for pc in problem_category:
                    l=[]
                    type= request.POST.get('toiletTypeSelect')
                    for toilet_type in toilet_types:
                        if toilet_type[0]==type:
                            title = '(Toilet Type:'+toilet_type[1]+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__type=type,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__type=type,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__type=type,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__type=type,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total+=sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)  
                stats = zip(stats,percentages) 
            if filter_category == 'Filter By Toilet Gender':
                stats = []
                for pc in problem_category:
                    l=[]
                    gender = request.POST.get('toiletGenderSelect')
                    for toilet_g in toilet_gender:
                        if toilet_g[0]==gender:
                            title = '(Toilet Gender:'+toilet_g[1]+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__sex=gender,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__sex=gender,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__sex=gender,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__sex=gender,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total+=sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)  
                stats = zip(stats,percentages) 
            if filter_category == 'Filter By Toilet Payment':
                stats = []
                for pc in problem_category:
                    l=[]
                    payment= request.POST.get('toiletPaymentSelect')
                    for toilet_payment in toilet_payments:
                        if toilet_payment[0]==payment:
                            title = '(Toilet Payment:'+toilet_payment[1]+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__payment=payment,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__payment=payment,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__payment=payment,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem__category=pc,toilet__payment=payment,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total+=sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)  
                stats = zip(stats,percentages) 
        else:
            filter_category = request.POST.get('filter_category')
            if filter_category == 'All':
                stats = []
                problems = Problem.objects.filter(category=selected_problem_category)
                for pc in problems:
                    l=[]
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem=pc,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem=pc,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total+=sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                    else:
                        l.append(pc.category.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)
                stats = zip(stats,percentages)
            
            if filter_category == 'Filter By Provider':
                stats = []
                problems = Problem.objects.filter(category=selected_problem_category)
                for pc in problems:
                    l=[]
                    provider_id = request.POST.get('providerSelect')
                    provider = Provider.objects.get(id=provider_id)
                    title = '(Provider:'+provider.user_profile.user.first_name+' '+provider.user_profile.user.last_name+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,provider=provider,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem=pc,provider=provider,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,provider=provider,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem=pc,provider=provider,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total += sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                    else:
                        l.append(pc.category.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)
                stats = zip(stats,percentages)
            if filter_category == 'Filter By Manager':
                stats = []
                problems = Problem.objects.filter(category=selected_problem_category)
                for pc in problems:
                    l=[]
                    manager_id = request.POST.get('managerSelect')
                    manager = Manager.objects.get(id=manager_id)
                    title = '(Manager:'+manager.user_profile.user.first_name+' '+manager.user_profile.user.last_name+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,provider__manager=manager,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem=pc,provider__manager=manager,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,provider__manager=manager,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem=pc,provider__manager=manager,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total += sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                    else:
                        l.append(pc.category.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)
                stats = zip(stats,percentages)
            if filter_category == 'Filter By Toilet ID':
                stats = []
                problems = Problem.objects.filter(category=selected_problem_category)
                for pc in problems:
                    l=[]
                    toilet_id = request.POST.get('toiletSelect')
                    toilet = Toilet.objects.get(id=toilet_id)
                    title = '(Toilet ID:'+toilet.toilet_id+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet=toilet,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet=toilet,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet=toilet,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem=pc,toilet=toilet,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total += sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                    else:
                        l.append(pc.category.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)
                stats = zip(stats,percentages)

            if filter_category == 'Filter By Toilet Location Code':
                stats = []
                problems = Problem.objects.filter(category=selected_problem_category)
                for pc in problems:
                    l=[]
                    location_code = request.POST.get('toiletLocationSelect')
                    title = '(Toilet Location Code:'+location_code+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__location_code=location_code,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__location_code=location_code,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__location_code=location_code,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem=pc,toilet__location_code=location_code,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total += sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                    else:
                        l.append(pc.category.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)
                stats = zip(stats,percentages)
            if filter_category == 'Filter By Toilet Area':
                stats = []
                problems = Problem.objects.filter(category=selected_problem_category)
                for pc in problems:
                    l=[]
                    area = request.POST.get('toiletAreaSelect')
                    for toilet_area in toilet_areas:
                        if toilet_area[0]==area:
                            title = '(Toilet Area:'+toilet_area[1]+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__area=area,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__area=area,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__area=area,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem=pc,toilet__area=area,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total += sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                    else:
                        l.append(pc.category.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)
                stats = zip(stats,percentages)
            if filter_category == 'Filter By Toilet Type':
                stats = []
                problems = Problem.objects.filter(category=selected_problem_category)
                for pc in problems:
                    l=[]
                    type = request.POST.get('toiletTypeSelect')
                    for toilet_type in toilet_types:
                        if toilet_type[0]==type:
                            title = '(Toilet Type:'+toilet_type[1]+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__type=type,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__type=type,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__type=type,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem=pc,toilet__type=type,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total += sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                    else:
                        l.append(pc.category.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)
                stats = zip(stats,percentages)
            if filter_category == 'Filter By Toilet Gender':
                stats = []
                problems = Problem.objects.filter(category=selected_problem_category)
                for pc in problems:
                    l=[]
                    gender = request.POST.get('toiletGenderSelect')
                    for toilet_g in toilet_gender:
                        if toilet_g[0]==gender:
                            title = '(Toilet Gender:'+toilet_g[1]+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__sex=gender,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__sex=gender,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__sex=gender,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem=pc,toilet__sex=gender,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total += sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                    else:
                        l.append(pc.category.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)
                stats = zip(stats,percentages)

            if filter_category == 'Filter By Toilet Payment':
                stats = []
                problems = Problem.objects.filter(category=selected_problem_category)
                for pc in problems:
                    l=[]
                    payment = request.POST.get('toiletPaymentSelect')
                    for toilet_payment in toilet_payments:
                        if toilet_payment[0]==payment:
                            title = '(Toilet Payment:'+toilet_payment[1]+')'
                    if startdate!='' and enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__payment=payment,timestamp__range= [startdate,enddate],status__in=status)
                    elif startdate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__payment=payment,timestamp__gte= startdate,status__in=status)
                    elif enddate!='':
                        tickets = Ticket.objects.filter(problem=pc,toilet__payment=payment,timestamp__lt= enddate,status__in=status)
                    else:
                        tickets = Ticket.objects.filter(problem=pc,toilet__payment=payment,status__in=status)
                    sum=0
                    for ticket in tickets:
                        sum+=ticket.complaints
                    total += sum
                    if pc.description!='others':
                        l.append(pc.description)
                        l.append(sum)
                        stats.append(l)
                    else:
                        l.append(pc.category.description)
                        l.append(sum)
                        stats.append(l)
                percentages = []
                for stat in stats:
                    if total!=0:
                        percentages.append(round(100 * float(stat[1])/float(total),2))
                    else:
                        percentages.append(0)
                stats = zip(stats,percentages)
        if status[0]=='0' and len(status)==1:
            status = 'Unresolved'
        elif status[0] == '1':
            status = 'resolved'
        elif status[0] == '2':
            status = 'Cannot Fix'
        elif status[0] == '3':
            status = 'Escalated'
        else:
            status = ''

        return render(request, 'administration/stats.html', {'user':user,'status':status,'title':title,'toilets':toilets,'toilet_locations':toilet_locations,'toilet_areas':toilet_areas,'toilet_types':toilet_types,'toilet_gender':toilet_gender,'toilet_payments':toilet_payments,'providers':providers,'managers':managers,'problem_category':problem_category,'stats':stats,})


"""
End: Views for managing toilets
"""
