# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-07 17:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0012_season_minimum_games'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='ranking_division',
            field=models.IntegerField(null=True),
        ),
    ]
