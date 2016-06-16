# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-15 13:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0006_problemcategory_is_audio_recording'),
    ]

    operations = [
        migrations.AddField(
            model_name='toilet',
            name='location_code',
            field=models.CharField(default=b'', max_length=10),
        ),
        migrations.AddField(
            model_name='toilet',
            name='payment',
            field=models.CharField(choices=[(b'P', b'Paid'), (b'F', b'Free')], default=b'F', max_length=1),
        ),
        migrations.AddField(
            model_name='toilet',
            name='sex',
            field=models.CharField(choices=[(b'B', b'Both'), (b'M', b'Male'), (b'F', b'Female')], default=b'B', max_length=1),
        ),
        migrations.AddField(
            model_name='toilet',
            name='type',
            field=models.CharField(choices=[(b'C', b'Communal'), (b'P', b'Public'), (b'S', b'School')], default=b'P', max_length=1),
        ),
    ]