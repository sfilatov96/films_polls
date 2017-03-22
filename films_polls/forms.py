# -*- coding: utf-8 -*-
from django import forms
from models import User, CustomUser, Film, Poll, Comment
from handler import send_email_confirmation
from MySQLdb import IntegrityError
import hashlib

from django.contrib import auth


class loginForm(forms.Form):
    username = forms.CharField(max_length=50, widget=forms.TextInput({"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput({"class": "form-control"}))
    redirect_to = forms.CharField(widget=forms.HiddenInput)

    def LoginUser(self, request):
        if self.is_valid():
            user = auth.authenticate(username=self.cleaned_data.get('username'),
                                     password=self.cleaned_data.get('password'))
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    redirect_to = self.cleaned_data.get("redirect_to")
                    return True, redirect_to
                else:
                    mistake = u"Почта вашего профиля не подтверждена! Пожалуйста подтвердите почту"
                    return False, mistake
            else:
                mistake = u"Email или пароль введены неверно! Пожалуйста, попробуйте заново!"
                return False, mistake
        else:
            print self.errors
            mistake = u"Форма не валидна"
            return False, mistake


class SignupForm(forms.Form):
    firstname = forms.CharField(max_length=50, widget=forms.TextInput({"class": "form-control"}))
    lastname = forms.CharField(max_length=50, widget=forms.TextInput({"class": "form-control"}))
    patronyc = forms.CharField(max_length=50, widget=forms.TextInput({"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput({"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput({"class": "form-control"}))
    repeat = forms.CharField(widget=forms.PasswordInput({"class": "form-control"}))

    def createUser(self):

        if self.is_valid():
            if not User.objects.filter(username=self.cleaned_data.get("email")):

                user = User.objects.create_user(username=self.cleaned_data.get("email"),
                                                password=self.cleaned_data.get("password"),
                                                email=self.cleaned_data.get("email"),
                                                first_name=self.cleaned_data.get("firstname"),
                                                last_name=self.cleaned_data.get("lastname"), is_active=False)
                customUser = CustomUser()
                user.save()
                h = hashlib.sha1('salt' + self.cleaned_data.get("email"))
                h = hashlib.sha1('salt' + h.hexdigest())
                key = h.hexdigest()
                customUser.user = user
                customUser.patronyc = self.cleaned_data.get("patronyc")
                customUser.key = key
                customUser.save()
                send_email_confirmation(self.cleaned_data.get("email"), key)
                return None
            else:
                mistake = u"Пользователь с таким именем email уже существует!"
                return mistake
        else:
            mistake = u"Регистрационная форма не валидна!"
            return mistake


class AddFilmForm(forms.Form):
    title = forms.CharField(max_length=50, widget=forms.TextInput({"class": "form-control"}))
    about = forms.CharField(widget=forms.Textarea({"class": "form-control"}))
    photo = forms.FileField()

    def createFilm(self):
        if self.is_valid():
            film = Film()
            film.title = self.cleaned_data.get("title")
            film.text = self.cleaned_data.get("about")
            film.photo = self.cleaned_data.get("photo")
            film.save()
            return False
        else:
            mistake = u"Форма заполнена с ошибками"
            return mistake

class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea({"class": "form-control"}))

    def addComment(self, request, page):
        user = auth.get_user(request)
        film = Film.objects.get(id=page)
        if not user.is_anonymous:
            user = CustomUser.objects.get(user=user)
            if self.is_valid():
                comm = Comment()
                comm.user = user
                comm.film = film
                comm.text = self.cleaned_data.get("comment")
                comm.save()
                return False
        else:
            mistake = u"Форма заполнена с ошибками"
            return mistake


class VoteForm(forms.Form):
    VOTE_CHOICES = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]
    vote = forms.ChoiceField(choices=VOTE_CHOICES, widget=forms.RadioSelect())

    def addVote(self, request, page):
        user = auth.get_user(request)
        film = Film.objects.get(id=page)
        if not user.is_anonymous:
            user = CustomUser.objects.get(user=user)
            if self.is_valid():
                poll = Poll()
                poll.user = user
                poll.film = film
                poll.mark = self.cleaned_data.get("vote")
                poll.save()
                return False
            else:
                mistake = u"Форма заполнена с ошибками"
                return mistake

