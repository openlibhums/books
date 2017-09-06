from django.conf.urls import url

from plugins.books import views

urlpatterns = [
    url(r'^$', views.index, name='books_index'),
    url(r'^(?P<book_id>\d+)/$', views.view_book, name='books_book'),
    url(r'^(?P<book_id>\d+)/format/(?P<format_id>\d+)/$', views.download_format, name='books_download_format'),

    url(r'^admin/$', views.admin, name='books_admin'),
    url(r'^admin/new/$', views.edit_book, name='books_new_book'),
    url(r'^admin/edit/(?P<book_id>\d+)/$', views.edit_book, name='books_edit_book'),
    url(r'^admin/edit/(?P<book_id>\d+)/contributor/$', views.edit_contributor, name='books_new_contributor'),
    url(r'^admin/edit/(?P<book_id>\d+)/contributor/(?P<contributor_id>\d+)$', views.edit_contributor,
        name='books_edit_contributor'),
    url(r'^admin/edit/(?P<book_id>\d+)/format/$', views.edit_format, name='books_new_format'),
    url(r'^admin/edit/(?P<book_id>\d+)/format/(?P<format_id>\d+)/$', views.edit_format, name='books_edit_format'),
]