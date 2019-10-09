# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def create_initial_region(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Region = apps.get_model("regions", "Region")
    Region.objects.create(name='Chicago', url='chicago')


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('url', models.SlugField(max_length=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RunPython(create_initial_region),
    ]
