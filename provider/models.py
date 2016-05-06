from django.db import models

from administration.models import Problem, Toilet, UserProfile
from manager.models import Manager


class Provider(models.Model):
    user_profile = models.OneToOneField(UserProfile, default=None, null=True)

    provider_id = models.CharField(max_length=100, unique=True, db_index=True)
    pin_code = models.CharField(max_length=10)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    toilets = models.ManyToManyField(Toilet, related_name='providers')
    problems = models.ManyToManyField(Problem, related_name='providers')

    def __unicode__(self):
        return str(self.user_profile.user.first_name) + '(' + self.user_profile.phone_number + ')'

    def delete(self, *args, **kwargs):
        self.user_profile.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    class Meta:
        index_together = ["provider_id", "pin_code"]
