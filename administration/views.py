from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route

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
