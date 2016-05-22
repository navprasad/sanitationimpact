# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-21 04:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0004_auto_20160506_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='type',
            field=models.CharField(choices=[(b'A', b'ADMINISTRATOR'), (b'M', b'MANAGER'), (b'P', b'PROVIDER')], default=b'P', max_length=1),
        ),
    ]