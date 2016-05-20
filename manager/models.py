from django.db import models
from administration.models import UserProfile


class Manager(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        self.user_profile.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def __unicode__(self):
        return str(self.user_profile.user.first_name) + ' (' + self.user_profile.phone_number + ')'
