# -*- coding: utf-8 -*-
# Generated by Django 1.9b1 on 2015-10-21 19:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('boundaries', '0005_auto_20150925_0338'),
        ('opencivicdata', '0004_auto_20150925_0338'),
    ]

    operations = [
        migrations.CreateModel(
            name='DivisionGeometry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boundary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='geometries', to='boundaries.Boundary')),
                ('division', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='geometries', to='opencivicdata.Division')),
            ],
        ),
    ]
