from django.db import models


class Ticket(models.Model):
    toilet_id = models.ForeignKey


class Issue(models.Model):
    description = models.CharField(max_length=255)