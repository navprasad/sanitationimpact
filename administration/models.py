from django.db import models
from django.contrib.auth.models import User


class Admin(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()

    def __unicode__(self):
        return self.name + '(' + self.phone_number + ')'


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


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    TYPE_CHOICES = (
        ('A', 'ADMINISTRATOR'),
        ('M', 'MANAGER'),
        ('P', 'PROVIDER')
    )
    type_choices = models.CharField(max_length=1, choices=TYPE_CHOICES)

    def __unicode__(self):
        return self.user.username
