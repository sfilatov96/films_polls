# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.http import HttpResponseNotAllowed
from django.contrib import auth
from django.core import serializers
from handler import chunks
import json
from .models import Film, CustomUser, Poll, Comment
from django.contrib.auth.models import User
from .forms import loginForm, SignupForm, AddFilmForm, CommentForm, VoteForm
from django.db.models import Count, Avg
from django.contrib.auth.decorators import login_required


def index(request, page=None):
    if request.POST.get("remove"):
        film = Film.objects.get(id=page)
        film.is_deleted = True
        film.save()
    if request.POST.get("update"):
        film = Film.objects.get(id=page)
        film.title = request.POST.get("title")
        film.text = request.POST.get("text")
        film.save()
    films = Film.objects.filter(is_deleted=False)
    for f in films:
        f.average = Poll.objects.filter(film=f).aggregate(Avg("mark"))
        f.cnt = Poll.objects.filter(film=f).count()
    if request.GET.get("order"):
        order = request.GET.get("order")
        if order == "alphabet":
            films = sorted(films, key=lambda x: x.title)
        elif order == "date":
            films = sorted(films, key=lambda x: x.pub_date, reverse=True)
        elif order == "rating":
            films = sorted(films, key=lambda x: x.average["mark__avg"], reverse=True)
        elif order == "popularity":
            films = sorted(films, key=lambda x: x.cnt, reverse=True)
        else:
            films = sorted(films, key=lambda x: x.pub_date, reverse=True)
    else:
        films = sorted(films, key=lambda x: x.pub_date, reverse=True)
    films = list(chunks(films, 3))
    return render(request, "films_polls/index.html", {"films": films})


def show_film_page(request, page):
    comment_form = CommentForm()
    vote_form = VoteForm()
    avg_vote = None
    all_votes = None
    count_vote = None
    is_voted = True
    user = auth.get_user(request)
    film = Film.objects.get(id=page)

    if not user.is_anonymous:
        c = CustomUser.objects.get(user=user)
        poll = Poll.objects.filter(user=c, film=film)
        if not poll:
            is_voted = False
    if is_voted:
        all_votes = Poll.objects.values("mark").filter(film=film).annotate(Count("mark")).order_by("mark")
        avg_vote = Poll.objects.filter(film=film).aggregate(Avg("mark"))
        count_vote = Poll.objects.filter(film=film).count()
        for i in all_votes:
            i["percent"] = 100 / count_vote * i["mark__count"]
    comments = Comment.objects.filter(is_deleted=False, film=film).order_by("pub_date")
    context = {"film": film, "is_voted": is_voted, "avg_vote": avg_vote, "all_votes": all_votes,
               "count_vote": count_vote, "comment_form": comment_form, "vote_form": vote_form}
    if comments:
        context.update({"comments": comments})
    return render(request, "films_polls/film.html", context)


def login(request):
    if request.GET.get("signup"):
        signup = request.GET.get("signup")
    if request.GET.get("next"):
        redirect_to = request.GET.get("next")
    else:
        redirect_to = "/"
    if request.POST:
        form = loginForm(request.POST, initial={"redirect_to": redirect_to})
        success, options = form.LoginUser(request)
        if success:
            return HttpResponseRedirect(options)
        else:
            return render(request, "films_polls/login.html",
                          context={"next": redirect_to, "form": form, "mistake": options})
    else:
        form = loginForm(initial={"redirect_to": redirect_to})
        return render(request, "films_polls/login.html", context={"next": redirect_to, "form": form, "signup":signup})


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


def signup(request):
    if request.POST:
        form = SignupForm(request.POST)
        error = form.createUser()
        if not error:
            return render(request, "films_polls/signup.html", {"success": True})
        else:
            return render(request, "films_polls/signup.html", {"mistake": error, "form": form})
    else:
        form = SignupForm()
        return render(request, "films_polls/signup.html", {"form": form})


@login_required(login_url="/login")
def add_film(request):
    if request.POST:
        form = AddFilmForm(request.POST, request.FILES)
        error = form.createFilm()
        if error:
            return render(request, "films_polls/add_film.html", {"form": form, "mistake": error})
        else:
            return render(request, "films_polls/add_film.html", {"form": form, "success": True})
    form = AddFilmForm()
    return render(request, "films_polls/add_film.html", {"form": form})


def users_films(request, user_id):
    films = Poll.objects.filter(film__is_deleted=False,  user__id=user_id)
    if films:
        user = films[0]
    else:
        user = User.objects.get(id=user_id)
    return render(request, "films_polls/users_films.html", {"films": films, "profile": user})


def api(request):
    films = Film.objects.filter(is_deleted=False)
    for f in films:
        f.average = Poll.objects.filter(film=f).aggregate(Avg("mark"))
        f.cnt = Poll.objects.filter(film=f).count()
    if request.GET.get("order"):
        order = request.GET.get("order")
        if order == "alphabet":
            films = sorted(films, key=lambda x: x.title)
        elif order == "date":
            films = sorted(films, key=lambda x: x.pub_date, reverse=True)
        elif order == "rating":
            films = sorted(films, key=lambda x: x.average["mark__avg"], reverse=True)
        elif order == "popularity":
            films = sorted(films, key=lambda x: x.cnt, reverse=True)
        else:
            films = sorted(films, key=lambda x: x.title)
    else:
        films = sorted(films, key=lambda x: x.title)
    data = serializers.serialize("json", films)
    return HttpResponse(data, content_type="application/json")


def remove_comment(request, id):
    user = auth.get_user(request)
    if request.POST.get("remove") and user.is_superuser:
        comm = Comment.objects.get(id=id)
        comm.is_deleted = True
        comm.save()
    answer = json.dumps({"query": "ok"})
    return HttpResponse(answer, content_type="application/json")


@login_required(login_url="/login")
def users(request, user_id=None):
    if request.POST.get("remove") and user_id:
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save()
    users = CustomUser.objects.filter(user__is_active=True)
    return render(request, "films_polls/users.html", {"users": users})


def activate(request):
    key = request.GET.get("key")
    if key:
        c = CustomUser.objects.filter(key=key).first()
        if c:
            c.user.is_active = True
            c.user.save()
            return HttpResponseRedirect("/login?signup=success")
        else:
            return render(request, "films_polls/signup.html",
                          context={"mistake": "Почта не подтверждена так как неверная ссылка."})

    else:
        return render(request, "films_polls/signup.html",
                      context={"mistake": "Почта не подтверждена так как неверная ссылка."})


def api_film(request, page):
    film = Film.objects.filter(id=page)
    if film:
        all_votes = Poll.objects.annotate(qty=Count("user_id")).filter(user__is_deleted=False, film=film)
        avg_vote = Poll.objects.filter(user__is_deleted=False, film=film).aggregate(Avg("mark"))
        count_vote = Poll.objects.filter(user__is_deleted=False, film=film).count()
        film.all_votes = all_votes
        film.avg_vote = avg_vote
        film.count_vote = count_vote
        data = serializers.serialize("json", film)
        return HttpResponse(data, content_type="application/json")
    else:
        answer = json.dumps({"answer": "film_not_found"})
        return HttpResponse(answer, content_type="application/json")


def add_comment(request, id):
    if request.POST:
        comment_form = CommentForm(request.POST)
        comment_form.addComment(request, id)
        return show_film_page(request, id)
    else:
        return HttpResponseNotAllowed("<h1>That method is not allowed!</h1>")


def vote(request, page):
    if request.POST:
        vote_form = VoteForm(request.POST)
        vote_form.addVote(request, page)
        return show_film_page(request, page)
    else:
        return HttpResponseNotAllowed("<h1>That method is not allowed!</h1>")


