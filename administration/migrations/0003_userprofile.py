# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-04 08:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('administration', '0002_auto_20160410_0331'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.ImageField(blank=True, upload_to=b'profile_images')),
                ('type', models.CharField(choices=[(b'A', b'ADMINISTRATOR'), (b'M', b'MANAGER'), (b'P', b'PROVIDER')], max_length=1)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
