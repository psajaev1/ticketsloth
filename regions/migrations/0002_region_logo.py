# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='logo',
            field=models.ImageField(default='logo', upload_to=b'regions/logos'),
            preserve_default=False,
        ),
    ]
