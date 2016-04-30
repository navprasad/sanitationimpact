from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from administration.forms import ToiletForm, UserForm, TicketForm, ProblemForm
from administration.models import Admin, ProblemCategory, Problem, Toilet
from administration.serializers import AdminSerializer, ProblemCategorySerializer, ProblemSerializer, ToiletSerializer


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
