# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-12 04:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='venue',
            name='tags',
        ),
        migrations.AddField(
            model_name='venue',
            name='alcohol_available',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='venue',
            name='coat_check_available',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='venue',
            name='food_available',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='venue',
            name='numbered_seats',
            field=models.BooleanField(default=False),
        ),
    ]
