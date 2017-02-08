from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

from plugins.books import models


def index(request):

    books = models.Book.objects.filter(date_published__isnull=False)

    template = 'books/index.html'
    context = {
        'books': books,
    }

    return render(request, template, context)

def book(request, book_id):

    book = get_object_or_404(models.Book, pk=book_id)

    template = 'books/book.html'
    context = {
        'book': book,
    }

    return render(request, template, context)


def download_format(request, book_id, format_id):

    book = get_object_or_404(models.Book, pk=book_id)
    format = get_object_or_404(models.Format, pk=format_id, book=book)

    # Handle serving the file here
    pass


@staff_member_required
def admin(request):

    books = models.Book.objects.all()

    template = 'books/admin.html'
    context = {
        'books': books,
    }

    return render(request, template, context)