# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-11 21:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('films_polls', '0006_poll'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patronyc', models.CharField(max_length=50)),
                ('is_deleted', models.BooleanField(default=0)),
                ('is_confirmed', models.BooleanField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='poll',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='films_polls.CustomUser'),
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.AddField(
            model_name='customuser',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
