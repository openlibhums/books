from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from utils.function_cache import cache


@cache(600)
def nav_hook(context):
    return '<li><a href="{url}"><i class="fa fa-book"></i> Books</a></li>'.format(
        url=reverse('books_admin')
    )
