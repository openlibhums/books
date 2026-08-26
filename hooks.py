from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from utils.function_cache import cache



@cache(600)
def nav_hook(context):
    return '<li><a href="{url}"><i class="fa fa-book"></i> Books</a></li>'.format(
        url=reverse('books_admin')
    )


def linked_books(context):
    request = context.get("request")
    preprint = context.get("preprint")

    if not preprint or not hasattr(preprint, "get_linked_books"):
        return ""

    theme = getattr(preprint.repository, "theme", "OLH")
    template_path = f"books/{theme}/repository_linked_books.html"

    books = preprint.get_linked_books()

    return mark_safe(render_to_string(
        template_path,
        {
            "preprint": preprint,
            "linked_books": books,
        },
        request=request,
    ))