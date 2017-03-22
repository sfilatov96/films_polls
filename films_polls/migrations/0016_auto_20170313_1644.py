# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-13 16:44
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('films_polls', '0015_auto_20170313_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='key',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='comment',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 13, 16, 44, 18, 676712)),
        ),
        migrations.AlterField(
            model_name='film',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 13, 16, 44, 18, 674166)),
        ),
    ]
