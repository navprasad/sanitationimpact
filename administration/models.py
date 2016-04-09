from django.db import models


class Admin(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()


class ProblemCategory(models.Model):
    index = models.IntegerField(unique=True, db_index=True)
    description = models.CharField(max_length=255)


class Problem(models.Model):
    index = models.IntegerField()
    description = models.CharField(max_length=255)
    category = models.ForeignKey(ProblemCategory, related_name='problems')

    class Meta:
        unique_together = ("index", "category")
        index_together = ["index", "category"]


class Toilet(models.Model):
    toilet_id = models.CharField(max_length=100, unique=True, db_index=True)
    address = models.TextField()
