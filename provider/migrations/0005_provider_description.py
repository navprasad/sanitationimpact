# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-16 05:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('provider', '0004_auto_20160522_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='provider',
            name='description',
            field=models.TextField(blank=True, default=b''),
        ),
    ]
