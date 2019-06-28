from django.contrib import admin

from plugins.books.models import *

admin_list = [
    (Book, ),
    (Contributor,),
    (Format,),
    (BookAccess,),
]

[admin.site.register(*t) for t in admin_list]
