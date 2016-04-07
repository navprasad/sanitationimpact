from django.db import models
from manager.models import Manager


class ProblemCategory(models.Model):
    index = models.IntegerField()
    description = models.CharField(max_length=255)

class Problem(models.Model):
    index = models.IntegerField()
    description = models.CharField(max_length=255)
    category = models.ForeignKey(ProblemCategory, related_name='problems')

class Toilet(models.Model):
    toilet_id = models.CharField(max_length=100, unique=True)
    address = models.TextField()

class Provider(models.Model):
    provider_id = models.CharField(max_length=100, unique=True)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    toilets = models.ManyToManyField(Toilet, related_name='providers')
    problems = models.ManyToManyField(Problem, related_name='providers')

