from django.db import models

from provider.models import Problem, Provider, Toilet

class Ticket(models.Model):
    UNRESOLVED = 0
    FIXED = 1
    WONTFIX = 2
    ESCALATED1 = 3
    ESCALATED2 = 4

    ticket_id = models.CharField(max_length=15)
    phone_number = models.CharField(max_length=15)
    timestamp = models.DateTimeField(auto_now_add=True)
    toilet = models.ForeignKey(Toilet, related_name='tickets')
    problem = models.ForeignKey(Problem, related_name='tickets')
    provider = models.ForeignKey(Provider, related_name='tickets')
    status = models.IntegerField(default=UNRESOLVED)

