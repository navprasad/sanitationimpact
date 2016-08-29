import uuid
from django.db import models

from administration.models import Problem, Toilet
from provider.models import Provider


class Ticket(models.Model):
    UNRESOLVED = 0
    FIXED = 1
    WONT_FIX = 2
    ESCALATED1 = 3
    ESCALATED2 = 4

    STATUS_CHOICES = (
        (0, 'Unresolved'),
        (1, 'Resolved'),
        (2, 'Cannot fix'),
        (3, 'Escalated'),
    )

    ticket_id = models.CharField(max_length=40, unique=True, db_index=True, default=uuid.uuid4)
    phone_number = models.CharField(max_length=15)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    toilet = models.ForeignKey(Toilet, related_name='tickets')
    problem = models.ForeignKey(Problem, related_name='tickets')
    provider = models.ForeignKey(Provider, related_name='tickets', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.IntegerField(default=UNRESOLVED)
    is_audio_present = models.BooleanField(default=False)
    is_provider_audio_present = models.BooleanField(default=False)
    provider_remarks = models.TextField(blank=True, default='')
    user_remarks = models.TextField(blank=True, default='')
    manager_remarks = models.TextField(blank=True, default='')
    complaints = models.IntegerField(default=1)
    additional_complaints_info = models.CharField(max_length=65000)
    

    def __unicode__(self):
        return str(self.id)

    class Meta:
        ordering = ['-timestamp']
