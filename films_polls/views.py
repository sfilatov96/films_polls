# -*- coding: utf-8 -*-
from django.shortcuts import render , HttpResponseRedirect,HttpResponse
from django.contrib import auth
from mysql_connect import connect
from MySQLdb import IntegrityError, cursors
from handler import chunks,send_email_confirmation
import json
from .models import  Film,CustomUser,Poll,Comment
from django.contrib.auth.models import User,user_logged_in
from django.db.models import Count, Avg
from django.contrib.auth.decorators import login_required



def index(request,page=None):
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
            films = sorted(films, key=lambda x: x.title)
    else:
        films = sorted(films, key=lambda x: x.title)
    films = list(chunks(films,3))
    return render(request,"films_polls/index.html",{"films":films})


def film(request, page):
    avg_vote = None
    all_votes = None
    count_vote = None
    is_voted = None
    film = Film.objects.get(id=page)
    user = auth.get_user(request)

    if not user.is_anonymous:
        user = CustomUser.objects.get(user=user)
        if request.POST:
            print request.POST.get("vote")
            if request.POST.get("vote"):
                poll = Poll()
                poll.user = user
                poll.film = film
                poll.mark = request.POST.get("vote")
                poll.save()
            if request.POST.get("comment"):
                comm = Comment()
                comm.user = user
                comm.film = film
                comm.text = request.POST.get("comment")
                comm.save()
        poll = Poll.objects.filter(user=user, film=film)
        if not poll:
            is_voted = False
        else:
            is_voted = True
    else:
        is_voted = True
    if is_voted:
        all_votes = Poll.objects.annotate(qty = Count("user_id")).filter(user__is_deleted=False,film=film)
        avg_vote = Poll.objects.filter(user__is_deleted=False,film=film).aggregate(Avg("mark"))
        count_vote = Poll.objects.filter(user__is_deleted=False,film=film).count()
        print avg_vote
        for i in all_votes:
            i.percent = 100/count_vote*i.qty
    comments = Comment.objects.filter(is_deleted=False,film=film).order_by("pub_date")
    context = {"film": film, "is_voted": is_voted, "avg_vote": avg_vote, "all_votes": all_votes,
                "count_vote": count_vote}
    if comments:
        context.update({"comments":comments})
    return render(request, "films_polls/film.html",context)


def login(request):
    if request.GET.get("next"):
        redirect_to = request.GET.get("next")
    else:
        redirect_to = "/"
    print redirect_to
    if request.POST:
        user = auth.authenticate(username=request.POST.get("email"),password=request.POST.get("password"))
        if user is not None:
            if user.is_active:
                auth.login(request,user)
                return HttpResponseRedirect(redirect_to)
            else:
                mistake = u"Почта вашего профиля не подтверждена! Пожалуйста подтвердите почту"
                return render(request, "films_polls/login.html",context={"mistake":mistake})
        else:
            mistake = u"Email или пароль введены неверно! Пожалуйста, попробуйте заново!"
            return render(request, "films_polls/login.html",context={"mistake":mistake})
    return render(request,"films_polls/login.html")


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


def signup(request):
    redirect_to = '/'
    if request.POST:
        r = request.POST
        user = User.objects.create_user(username=r.get("email"), password=r.get("password"),
                                        email=r.get("email"), first_name=r.get("first_name"),
                                        last_name=r.get("last_name"))
        customUser = CustomUser()
        user.save()
        customUser.user = user
        customUser.patronyc = r.get("patronyc")
        customUser.save()
        return HttpResponseRedirect(redirect_to)

    return render(request,"films_polls/signup.html")

@login_required(login_url="/login")
def add_film(request):
    if request.POST:
        film = Film()
        film.title = request.POST["title"]
        film.text = request.POST["about"]
        film.photo = request.FILES["photo"]
        film.save()
        return HttpResponseRedirect("/")
    return render(request, "films_polls/add_film.html")





def users_films(request,user_id):

    # cursor.execute("""SELECT * FROM films_polls_film f INNER join polls p
    # INNER JOIN users u on (u.id=p.user_id) and (p.film_id=f.id)  WHERE u.id=%s AND f.is_deleted = false and u.is_deleted = false""", (user_id,),)
    films = Poll.objects.filter(film__is_deleted=False,user__is_deleted=False,user__id=user_id)
    if films:
        user = films[0]
    else :
        user = User.objects.get(id=user_id)
    return render(request, "films_polls/users_films.html",{"films":films,"profile":user})


def api(request):
    order = "alphabet"
    if request.GET:
        try:
            order = request.GET["order"]

        except:
            order = "alphabet"
    db = connect()
    cursor = db.cursor(cursors.DictCursor)
    print order
    if order == "alphabet":
        sort = "title ASC"
    if order == "date":
        sort = "pub_date DESC"
    if order == "rating":
        sort = "average DESC"
    if order == "popularity":
        sort = "cnt DESC"

    query = """select * from (select film_id,count(user_id) as cnt,avg(mark) as average from polls 
             where user_id is not null group by film_id  order by cnt desc) c inner join films_polls_film f  on f.id = c.film_id order by """ + sort
    cursor.execute(query)
    result = cursor.fetchall()
    for r in result:
        r["average"] = int(r["average"])
        r["pub_date"] = str(r["pub_date"])
    lst = list(chunks(result, 3))
    answer = json.dumps(lst)
    return HttpResponse(answer,content_type="application/json")


def comment(request,id):
    user = auth.get_user(request)
    if request.POST.get("remove") and user.is_superuser:
        comm = Comment.objects.get(id=id)
        comm.is_deleted = True
        comm.save()
    answer = json.dumps({"query":"ok"})
    return HttpResponse(answer, content_type="application/json")


@login_required(login_url="/login")
def users(request,user_id=None):
    if request.POST.get("remove") and user_id:
        user = User.objects.get(id=user_id)
        user.is_active = False
        user.save()
    users = CustomUser.objects.filter(user__is_active=True)
    return render(request,"films_polls/users.html",{"users":users})


def activate(request):
    key = request.GET.get("key")
    if key:
        db = connect()
        cursor = db.cursor(cursors.DictCursor)
        cursor.execute("select email from users_confirmation where `key`=%s", (key,),)
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE users set is_confirmed = true where email=%s", (result.get("email"),),)
            cursor.close()
            db.commit()
            db.close()
        else:
            return render(request, "films_polls/signup.html",context={"mistake":"Почта не подтверждена так как неверная ссылка."})
    return HttpResponseRedirect("/login")


def api_film(request,page):
    db = connect()
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute("""SELECT * FROM films_polls_film WHERE id=%s AND is_deleted=false""", (page,))
    result = cursor.fetchone()
    if result:
        cursor.execute(
            """select mark,count(user_id) as users_count from  polls p inner join users u on u.id = p.user_id where film_id=%s and u.is_deleted = false group by mark """,
            (page,))
        all_votes = cursor.fetchall()
        cursor.execute(
            """select avg(mark) as average_vote from  polls p inner join users u on u.id = p.user_id  where film_id = %s and u.is_deleted = false""",
            (page,))
        avg_vote = cursor.fetchone()
        cursor.execute(
            """select count(*) as votes from  polls  p inner join users u on u.id = p.user_id where film_id = %s and u.is_deleted = false""",
            (page,))
        count_vote = cursor.fetchone()
        result.update({"users_votes":all_votes})
        result.update(avg_vote)
        result.update(count_vote)
        result["average_vote"] = int(result["average_vote"])
        result["pub_date"] = str(result["pub_date"])
        answer = json.dumps({"answer": result})
        return HttpResponse(answer, content_type="application/json")
    else:
        answer = json.dumps({"answer": "film_not_found"})

        return HttpResponse(answer, content_type="application/json")
