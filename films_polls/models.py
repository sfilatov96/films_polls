from __future__ import unicode_literals
import datetime

from django.db import models
from django.contrib.auth.models import User
class Film(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    photo = models.ImageField(upload_to='films_polls/%Y/%m/%d')
    pub_date = models.DateTimeField(default=datetime.datetime.now())
    is_deleted = models.BooleanField(default=0)
    def __unicode__(self):
        return self.title


class CustomUser(models.Model):
    user = models.OneToOneField(User)
    patronyc = models.CharField(max_length=50,null=False)
    is_deleted = models.BooleanField(default=0)
    is_confirmed = models.BooleanField(default=0)
    def __unicode__(self):
        return self.user.username

class Poll(models.Model):
    user_id = models.ForeignKey("CustomUser",on_delete=models.CASCADE)
    film_id = models.ForeignKey("Film",on_delete=models.CASCADE)
    mark_id = models.IntegerField(null=False)
