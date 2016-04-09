from django.db import models

from admin.models import Problem, Toilet
from manager.models import Manager


class Provider(models.Model):
    provider_id = models.CharField(max_length=100, unique=True, db_index=True)
    pin_code = models.CharField(max_length=10)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    toilets = models.ManyToManyField(Toilet, related_name='providers')
    problems = models.ManyToManyField(Problem, related_name='providers')

    class Meta:
        index_together = ["provider_id", "pin_code"]
