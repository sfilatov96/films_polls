# -*- coding: utf-8 -*-
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kinorating.settings")

import django
django.setup()
from films_polls.models import *
import random
from loremipsum import get_paragraphs



PASSWORD = "password"
PATRONYC = ["Андреевич","Михайлович","Викторович","Сергеевич","Петрович"]
NAMES = ["Игорь","Петр","Олег","Александр","Владимир","Андрей","Артём","Иван","Михаил","Дмитрий","Константин","Павел"]
FIRSTNAMES = ["Кириллов","Петров","Скворцов","Александров","Владимирский","Андреев","Артёмов","Иванов","Михеев","Дмитриев","Константинов","Павлов"]
EMAILS = ["worlder@mail.ru","offset@mail.ru","vldos@yandex.ru","ptichka@mail.ru","python@yandex.ru","vales@yandex.ru","borland@yandex.ru","keyword@yandex.ru","friends@yandex.ru","kok@mail.ru","lublu-filmy@yandex.ru"]
def create_users():
    for e in EMAILS:
        user = User.objects.create_user(username=e,
                                        password=PASSWORD,
                                        email=e,
                                        first_name=random.choice(FIRSTNAMES),
                                        last_name=random.choice(NAMES), is_active=True)
        customUser = CustomUser()
        user.save()
        customUser.user = user
        customUser.patronyc = random.choice(PATRONYC)
        customUser.save()

def add_votes():
    films = Film.objects.all()
    users = CustomUser.objects.all()
    for f in films:
        for u in users:
            poll = Poll()
            poll.user = u
            poll.film = f
            poll.mark = random.randint(1,10)
            poll.save()

def add_comment():
    films = Film.objects.all()
    users = CustomUser.objects.all()
    for f in films:
        for r in range(0,random.randint(1,3)):
            comm = Comment()
            comm.film = f
            comm.user = random.choice(users)
            comm.text = get_paragraphs(random.randint(1,4))
            comm.save()


add_comment()