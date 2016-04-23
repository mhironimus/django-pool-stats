# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-02 18:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0006_auto_20160402_1751'),
    ]

    operations = [

        migrations.DeleteModel(
            name='AwayLineupEntry',
        ),
        migrations.DeleteModel(
            name='HomeLineupEntry',
        ),
        migrations.AddField(
            model_name='lineupentry',
            name='position',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='stats.PlayPosition'),
        ),
        migrations.CreateModel(
            name='AwayLineupEntry',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('stats.lineupentry',),
        ),
        migrations.CreateModel(
            name='HomeLineupEntry',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('stats.lineupentry',),
        ),
    ]
