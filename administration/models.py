from django.db import models


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
