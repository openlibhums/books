from django.contrib import admin

from plugins.books.models import *


class ChapterAdmin(admin.ModelAdmin):
    """Displays objects in the Django admin interface."""
    list_display = ('title', 'number', 'book', 'pages', 'doi')
    list_filter = ('book',)
    search_fields = ('title',)
    raw_id_fields = ('book',)
    filter_horizontal = ('contributors',)


class BookAccessAdmin(admin.ModelAdmin):
    list_display = ('book', 'chapter', 'type', 'format', 'country', 'accessed')
    list_filter = ('book',)
    search_fields = ('book__title',)


admin_list = [
    (Book, ),
    (Contributor,),
    (Format,),
    (BookAccess, BookAccessAdmin),
    (Chapter, ChapterAdmin),
]

[admin.site.register(*t) for t in admin_list]
