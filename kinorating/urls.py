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
    url(r'^film/(?P<page>\d+)?/?', views.film, name='film'),
    url(r'^users_film/(?P<user_id>\d+)?/?', views.users_films, name='users_films'),
    url(r'^add_film/?', views.add_film, name='add_film'),
    url(r'^api/?', views.api, name='api'),
    url(r'^(?P<page>\d+)?/?', views.index, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
