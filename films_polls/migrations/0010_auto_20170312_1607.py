# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-12 16:07
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('films_polls', '0009_auto_20170312_1604'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='film_id',
            new_name='film',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='user_id',
            new_name='user',
        ),
        migrations.AlterField(
            model_name='film',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 3, 12, 16, 7, 17, 558731)),
        ),
    ]
