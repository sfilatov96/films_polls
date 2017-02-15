from __future__ import unicode_literals

from django.db import models

class Film(models.Model):
    title = models.CharField(max_length = 255)
    text = models.TextField()
    photo = models.ImageField(upload_to = 'films_polls/%Y/%m/%d')
    def __unicode__(self):
        return self.title
