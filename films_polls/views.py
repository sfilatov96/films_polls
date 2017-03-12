# -*- coding: utf-8 -*-
from django.shortcuts import render , HttpResponseRedirect,HttpResponse
from django.contrib import auth
from mysql_connect import connect
from MySQLdb import IntegrityError, cursors
from handler import chunks,send_email_confirmation
import json
from .models import  Film,CustomUser
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required



def index(request,page=None):
    lst = []
    films = Film.objects.all()
    # order = "alphabet"
    #
    # db = connect()
    # cursor = db.cursor(cursors.DictCursor)
    # if request.GET:
    #     try:
    #         order = request.GET["order"]
    #
    #     except:
    #         order = "alphabet"
    # if(request.session.get("id")):
    #     cursor.execute("""SELECT * FROM users WHERE id=%s and is_deleted =false""", (request.session["id"],), )
    #     if not cursor.fetchone():
    #         logout(request)
    # if request.POST.get("remove"):
    #     cursor.execute("""UPDATE films_polls_film set is_deleted = true where id=%s """, (page,))
    # if request.POST.get("update"):
    #     print (page),request.POST.get("title"),request.POST.get("text")
    #     cursor.execute("""UPDATE films_polls_film set title = %s,text = %s where id = %s """, (request.POST.get("title"),request.POST.get("text"),page,))
    # print order
    # if order == "alphabet":
    #     sort = "title ASC"
    # if order == "date":
    #     sort = "pub_date DESC"
    # if order == "rating":
    #     sort = "average DESC"
    # if order == "popularity":
    #     sort = "cnt DESC"
    #
    # query = """select * from (select film_id,count(user_id) as cnt,avg(mark) as average from polls p
    #       left join users u on p.user_id = u.id where u.is_deleted = false or p.user_id is NULL group by film_id  order by cnt desc) c inner join films_polls_film f
    #        on f.id = c.film_id where f.is_deleted = false order by """ + sort
    # cursor.execute(query)
    #
    # result = cursor.fetchall()
    # cursor.close()
    # db.commit()
    # db.close()

    films = list(chunks(films,3))
    print films
    return render(request,"films_polls/index.html",{"films":films})


def film(request, page):
    if request.session.get("id"):
        avg_vote = None
        is_admin = None
        all_votes = None
        count_vote = None
        db = connect()
        cursor = db.cursor(cursors.DictCursor)
        if request.POST:
            try:
                cursor.execute("""INSERT INTO polls(user_id,film_id,mark) VALUES (%s,%s,%s)""", (request.session["id"], page, request.POST["vote"]),)
            except KeyError:
                pass
            try:
                cursor.execute("""INSERT INTO main_comments(user_id,film_id,comment) VALUES (%s,%s,%s)""", (request.session["id"], page, request.POST["comment"]),)
            except KeyError:
                pass

        if request.session.get("is_superuser"):
            is_admin = True

        cursor.execute("""SELECT * FROM films_polls_film WHERE id=%s AND is_deleted=false""",(page,))
        result = cursor.fetchone()
        if result:
            cursor.execute("""SELECT * FROM polls WHERE film_id=%s AND user_id=%s """, (page,request.session["id"]))
            is_voted = cursor.fetchone()
            if not is_voted:
                is_voted = False

            else:
                is_voted = True
                cursor.execute("""select mark,count(user_id) as qty from  polls p inner join users u on u.id = p.user_id where film_id=%s and u.is_deleted = false group by mark """, (page,))
                all_votes = cursor.fetchall()
                cursor.execute("""select avg(mark) as average from  polls p inner join users u on u.id = p.user_id  where film_id = %s and u.is_deleted = false""",(page,))
                avg_vote = cursor.fetchone()
                cursor.execute("""select count(*) as cnt from  polls  p inner join users u on u.id = p.user_id where film_id = %s and u.is_deleted = false""", (page,))
                count_vote = cursor.fetchone()

                for i in all_votes:
                    i.update({"percent":(100/count_vote["cnt"]*i["qty"])})

            cursor.execute("""SELECT * FROM main_comments m INNER JOIN users u on u.id = m.user_id  WHERE film_id=%s and m.is_deleted = false and u.is_deleted = false ORDER BY pub_date ASC""", (page,))
            comments = cursor.fetchall()


            cursor.close()
            db.commit()
            db.close()
            print is_admin
            context = {"film": result, "is_voted": is_voted, "avg_vote": avg_vote, "all_votes": all_votes, "count_vote": count_vote, "is_admin":is_admin}
            if comments:
                context.update({"comments":comments})
            return render(request,"films_polls/film.html",context,)
        else:
            return render(request, "films_polls/film.html")
    else:
        return HttpResponseRedirect("/login")


def login(request):
    if request.POST:
        user = auth.authenticate(username=request.POST.get("email"),password="258147")
        print user
        if user is not None:
            if user.is_active:
                auth.login(request,user)
                return HttpResponseRedirect("/")
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

@login_required
def add_film(request):
        if request.POST:
            # db = connect()
            # cursor = db.cursor(cursors.DictCursor)
            film = Film()
            film.title = request.POST["title"]
            film.text = request.POST["about"]
            film.photo = request.FILES["photo"]
            print film
            film.save()
            # cursor.execute("""SELECT id FROM films_polls_film WHERE title=%s and text=%s""", (request.POST["title"], request.POST["about"],))
            # result = cursor.fetchone()
            # cursor.execute("""INSERT INTO polls(film_id,mark) VALUES (%s,%s)""", (result["id"],0))
            # cursor.close()
            # db.commit()
            # db.close()
            return HttpResponseRedirect("/")
        return render(request, "films_polls/add_film.html")





def users_films(request,user_id):
    db = connect()
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute("""SELECT * FROM films_polls_film f INNER join polls p 
    INNER JOIN users u on (u.id=p.user_id) and (p.film_id=f.id)  WHERE u.id=%s AND f.is_deleted = false and u.is_deleted = false""", (user_id,),)
    users = cursor.fetchall()
    if users:
        user = users[0]
    else :
        cursor.execute("""SELECT * FROM  users  WHERE id=%s AND is_deleted = false""", (user_id,), )
        user = cursor.fetchone()

    return render(request, "films_polls/users_films.html",{"users":users,"user":user})


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
    db = connect()
    cursor = db.cursor(cursors.DictCursor)
    cursor.execute("""UPDATE main_comments set is_deleted = true where id = %s""",(id,))
    cursor.close()
    db.commit()
    db.close()
    answer = json.dumps({"query":"ok"})
    return HttpResponse(answer, content_type="application/json")

def users(request,user_id=None):
    db = connect()
    cursor = db.cursor(cursors.DictCursor)
    is_admin = None
    if request.session.get("is_superuser"):
        is_admin = True
    if request.POST.get("remove") and user_id:
        cursor.execute("""UPDATE users set is_deleted=true where id=%s """,(user_id,))
    cursor.execute("""SELECT * FROM  users where is_deleted = false""")
    users = cursor.fetchall()
    cursor.close()
    db.commit()
    db.close()
    return render(request,"films_polls/users.html",{"users":users,"is_admin":is_admin})


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
