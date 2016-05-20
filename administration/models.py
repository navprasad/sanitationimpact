from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver


class UserProfile(models.Model):
    TYPE_CHOICES = (
        ('A', 'ADMINISTRATOR'),
        ('M', 'MANAGER'),
        ('P', 'PROVIDER')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile_images', blank=True)
    phone_number = models.CharField(max_length=20, null=True)
    address = models.TextField(null=True)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES, default='P')

    def delete(self, *args, **kwargs):
        self.user.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, **kwargs):
    instance = kwargs['instance']
    if kwargs['created']:  # create
        UserProfile.objects.get_or_create(user=instance)


class Admin(models.Model):
    user_profile = models.OneToOneField(UserProfile, default=None, null=True)

    def delete(self, *args, **kwargs):
        self.user_profile.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.user_profile.user.username


class ProblemCategory(models.Model):
    index = models.IntegerField(unique=True, db_index=True)
    description = models.CharField(max_length=255)

    def __unicode__(self):
        return str(self.index) + ': ' + self.description

    class Meta:
        ordering = ('index',)


class Problem(models.Model):
    index = models.IntegerField(db_index=True)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(ProblemCategory, related_name='problems')

    def __unicode__(self):
        return str(self.index) + ': ' + self.description + '(' + self.category.description + ')'

    class Meta:
        unique_together = ("index", "category")
        index_together = ["index", "category"]
        ordering = ('index',)


class Toilet(models.Model):
    toilet_id = models.CharField(max_length=100, unique=True, db_index=True)
    address = models.TextField()

    def __unicode__(self):
        return str(self.toilet_id) + ': ' + self.address

