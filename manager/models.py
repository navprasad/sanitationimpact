from django.db import models
from administration.models import UserProfile


class Manager(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    manager_id = models.CharField(max_length=100, unique=True, db_index=True)
    pin_code = models.CharField(max_length=10)
    description = models.TextField(blank=True, default='')

    def delete(self, *args, **kwargs):
        self.user_profile.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def __unicode__(self):
        return str(self.user_profile.user.first_name) + ' (' + self.user_profile.phone_number + ')'

    class Meta:
        index_together = ["manager_id", "pin_code"]
