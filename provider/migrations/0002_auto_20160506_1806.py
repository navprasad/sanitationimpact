# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-06 12:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0004_auto_20160506_1806'),
        ('provider', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='provider',
            name='address',
        ),
        migrations.RemoveField(
            model_name='provider',
            name='name',
        ),
        migrations.RemoveField(
            model_name='provider',
            name='phone_number',
        ),
        migrations.AddField(
            model_name='provider',
            name='user_profile',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='administration.UserProfile'),
        ),
    ]
