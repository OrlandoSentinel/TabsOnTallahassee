# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-15 06:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preferences', '0004_auto_20151022_0220'),
    ]

    operations = [
        migrations.AddField(
            model_name='preferences',
            name='email_frequency',
            field=models.CharField(choices=[('N', 'Never'), ('D', 'Daily'), ('W', 'Weekly')], default='N', max_length=1),
        ),
        migrations.AddField(
            model_name='preferences',
            name='email_type',
            field=models.CharField(choices=[('H', 'HTML'), ('T', 'Plain Text')], default='T', max_length=1),
        ),
    ]
