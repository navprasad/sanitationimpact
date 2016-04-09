# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-09 11:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('provider', '0001_initial'),
        ('reporting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=255)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='provider.Provider')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reporting.Ticket')),
            ],
        ),
    ]
