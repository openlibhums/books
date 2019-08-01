from django.contrib import admin

from plugins.books.models import *


class ChapterAdmin(admin.ModelAdmin):
    """Displays objects in the Django admin interface."""
    list_display = ('title', 'number', 'book', 'pages', 'doi')
    list_filter = ('book',)
    search_fields = ('title',)
    raw_id_fields = ('book',)
    filter_horizontal = ('contributors',)


admin_list = [
    (Book, ),
    (Contributor,),
    (Format,),
    (BookAccess,),
    (Chapter, ChapterAdmin),
]

[admin.site.register(*t) for t in admin_list]
