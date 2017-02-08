from django.conf.urls import url

from plugins.books import views

urlpatterns = [
    url(r'^$', views.index, name='books_index'),
]