from django.db import models
from administration.models import UserProfile


class Manager(models.Model):
    MANAGER_CODE_CHOICES = (
        ('MC', 'MC: Municipal Commissioner'),
        ('MHO', 'MHO: Municipal Health Officer'),
        ('MSI', 'MSI: Municipal Sanitary Inspecter'),
        ('SS', 'SS: Sanitary Supervisor'),
        ('DRDA', 'DRDA: District Rural Development Agent'),
        ('BDO', 'BDO: Block District Officer'),
        ('TSC', 'TSC: Total Sanitation Coordinator (Block)'),
        ('SHM', 'SHM: School Head Master/Mistress')
    )

    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)

    manager_id = models.CharField(max_length=100, unique=True, db_index=True)
    pin_code = models.CharField(max_length=10)
    description = models.TextField(blank=True, default='')
    manager_code = models.CharField(max_length=5, choices=MANAGER_CODE_CHOICES, default='MC')

    def delete(self, *args, **kwargs):
        self.user_profile.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def __unicode__(self):
        return str(self.user_profile.user.first_name) + ' (' + self.user_profile.phone_number + ')'

    class Meta:
        index_together = ["manager_id", "pin_code"]
