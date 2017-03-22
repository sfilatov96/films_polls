"""kinorating URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from films_polls import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/?', views.login, name='login'),
    url(r'^logout/?', views.logout, name='logout'),
    url(r'^signup/?', views.signup, name='signup'),
    url(r'^activate/?', views.activate, name='activate'),
    url(r'^film/(?P<page>\d+)?/?', views.show_film_page, name='film'),
    url(r'^comment/remove/(?P<id>\d+)?/?', views.remove_comment, name='remove_comment'),
    url(r'^comment/add/(?P<id>\d+)?/?', views.add_comment, name='add_comment'),
    url(r'^users_films/(?P<user_id>\d+)?/?', views.users_films, name='users_films'),
    url(r'^add_film/?', views.add_film, name='add_film'),
    url(r'^users/(?P<user_id>\d+)?/??', views.users, name='users'),
    url(r'^api/film/(?P<page>\d+)/?', views.api_film, name='api_film'),
    url(r'^vote/(?P<page>\d+)?/?', views.vote, name='vote'),
    url(r'^api/?', views.api, name='api'),
    url(r'^(?P<page>\d+)?/?', views.index, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
