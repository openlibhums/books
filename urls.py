from django.urls import re_path

from plugins.books import views

urlpatterns = [
    re_path(r'^$', views.index, name='books_index'),
    re_path(r'^category/(?P<category_slug>[-\w.]+)/$', views.index, name='books_index_category'),
    re_path(r'^(?P<book_id>\d+)/$', views.view_book, name='books_book'),
    re_path(r'^(?P<book_id>\d+)/format/(?P<format_id>\d+)/$', views.download_format, name='books_download_format'),
    re_path(r'^(?P<book_id>\d+)/format/(?P<format_id>\d+)/mark_download/(?P<mark_download>no|yes)/$', views.download_format, name='books_download_format'),
    re_path(r'^(?P<book_id>\d+)/format/(?P<format_id>\d+)/read/$', views.read_epub, name='books_read_epub'),
    re_path(r'^(?P<book_id>\d+)/chapter/(?P<chapter_id>\d+)$',
        views.view_chapter,
        name='book_view_chapter'),
    re_path(r'^(?P<book_id>\d+)/format/(?P<chapter_id>\d+)/download/$',
        views.download_chapter,
        name='books_download_chapter'),

    re_path(r'^admin/$', views.admin, name='books_admin'),
    re_path(r'^admin/categories/$', views.categories, name='books_categories'),
    re_path(r'^admin/categories/(?P<category_id>\d+)$', views.categories, name='books_edit_category'),
    re_path(r'^admin/new/$', views.edit_book, name='books_new_book'),
    re_path(r'^admin/edit/(?P<book_id>\d+)/$', views.edit_book, name='books_edit_book'),
    re_path(r'^admin/edit/(?P<book_id>\d+)/contributor/$', views.edit_contributor, name='books_new_contributor'),
    re_path(r'^admin/edit/(?P<book_id>\d+)/contributor/(?P<contributor_id>\d+)$', views.edit_contributor,
        name='books_edit_contributor'),
    re_path(r'^admin/edit/(?P<book_id>\d+)/format/$', views.edit_format, name='books_new_format'),
    re_path(r'^admin/edit/(?P<book_id>\d+)/format/(?P<format_id>\d+)/$', views.edit_format, name='books_edit_format'),

    re_path(r'^admin/edit/(?P<book_id>\d+)/chapter/new/$',
        views.books_chapter,
        name='books_new_chapter'),
    re_path(r'^admin/edit/(?P<book_id>\d+)/chapter/edit/(?P<chapter_id>\d+)/$',
        views.books_chapter,
        name='books_edit_chapter'),

    re_path(r'^admin/import/$', views.import_books_upload, name='books_import_books_upload'),
    re_path(r'^admin/import/(?P<uuid>.+)/process/$', views.import_books_process, name='books_import_process'),
    re_path(r'^admin/import/(?P<uuid>.+)/$', views.import_books_preview, name='books_import_preview'),

    re_path(r'^admin/metrics/$', views.book_metrics, name='books_metrics'),
    re_path(r'^admin/metrics/by_month/$', views.book_metrics_by_month, name='books_metrics_by_month'),

    re_path(r'^onix/export/$', views.export_onix_xml, name='books_export_onix_xml'),
    re_path(r'^onix/export/(?P<book_id>\d+)/$', views.export_onix_xml, name='books_export_onix_xml_book'),
]