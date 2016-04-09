from django.db import models

from admin.models import Problem, Toilet
from provider.models import Provider


class Ticket(models.Model):
    UNRESOLVED = 0
    FIXED = 1
    WONT_FIX = 2
    ESCALATED1 = 3
    ESCALATED2 = 4

    ticket_id = models.CharField(max_length=15, unique=True, db_index=True)
    phone_number = models.CharField(max_length=15)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    toilet = models.ForeignKey(Toilet, related_name='tickets')
    problem = models.ForeignKey(Problem, related_name='tickets')
    status = models.IntegerField(default=UNRESOLVED)
