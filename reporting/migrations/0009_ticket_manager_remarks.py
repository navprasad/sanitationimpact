# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-07-27 05:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0008_auto_20160616_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='manager_remarks',
            field=models.TextField(blank=True, default=b''),
        ),
    ]
