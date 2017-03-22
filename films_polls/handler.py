# -*- coding: utf-8 -*-

from django.core.mail import send_mail
from mysql_connect import connect
from MySQLdb import cursors
import hashlib

def chunks(lst, count):
    for i in range(0,len(lst),3):
        yield lst[i:i+3]


def send_email_confirmation(email, key):
    email_subject = 'Подтверждение email-адреса на сайте FilmsPolls.tk'
    email_body = """Чтобы подтвердить email пожалуйста пройдите по ссылке ниже \n
    http://filmspolls.tk/activate?key=%s""" % (key)
    send_mail(email_subject, email_body, 'myemail@example.com',
              [email], fail_silently=False)
