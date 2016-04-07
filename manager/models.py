from django.db import models


class Manager(models.Model):
    manager_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
