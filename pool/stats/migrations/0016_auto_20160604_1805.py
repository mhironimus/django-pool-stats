# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-06-04 18:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0015_playposition_tiebreaker'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='match',
            options={'verbose_name': 'Match', 'verbose_name_plural': 'Matches'},
        ),
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='team',
            name='rank_tie_breaker',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='ranking',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
