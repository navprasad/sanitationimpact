from django.db import models
from manager.models import Manager


class Provider(models.Model):
    provider_id = models.CharField(max_length=100, unique=True)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)


class Toilet(models.Model):
    toilet_id = models.CharField(max_length=100, unique=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
