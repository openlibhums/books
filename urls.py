from django.conf.urls import url

from plugins.books import views

urlpatterns = [
    url(r'^$', views.index, name='books_index'),
    url(r'^book/(?P<book_id>\d+)/$', views.book, name='books_book'),
    url(r'^book/(?P<book_id>\d+)/format/(?P<format_id>\d+)/$', views.download_format, name='books_download_format'),
    url(r'^admin/$', views.admin, name='books_admin'),
]