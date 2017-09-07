from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.contrib.admin.views.decorators import staff_member_required

from plugins.books import models, forms, files


def index(request):

    books = models.Book.objects.filter(date_published__isnull=False)

    template = 'books/index.html'
    context = {
        'books': books,
    }

    return render(request, template, context)


def view_book(request, book_id):

    book = get_object_or_404(models.Book, pk=book_id, date_published__isnull=False)

    template = 'books/book.html'
    context = {
        'book': book,
    }

    return render(request, template, context)


def download_format(request, book_id, format_id):

    book = get_object_or_404(models.Book, pk=book_id, date_published__isnull=False)
    format = get_object_or_404(models.Format, pk=format_id, book=book)

    # Handle serving the file here
    return files.serve_book_file(format)


@staff_member_required
def admin(request):

    books = models.Book.objects.all()

    template = 'books/admin.html'
    context = {
        'books': books,
    }

    return render(request, template, context)


@staff_member_required
def edit_book(request, book_id=None):

    book = None

    if book_id:
        book = get_object_or_404(models.Book, pk=book_id)

    form = forms.BookForm(instance=book)

    if request.POST:
        form = forms.BookForm(request.POST, request.FILES, instance=book)

        if form.is_valid():
            form.save()

            return redirect(reverse('books_admin'))

    template = 'books/edit_book.html'
    context = {
        'book': book,
        'form': form,
    }

    return render(request, template, context)


@staff_member_required()
def edit_contributor(request, book_id, contributor_id=None):

    contributor = None
    book = get_object_or_404(models.Book, pk=book_id)

    if contributor_id:
        contributor = get_object_or_404(models.Contributor, pk=contributor_id, book=book)

    form = forms.ContributorForm(instance=contributor, book=book)

    if request.POST:
        form = forms.ContributorForm(request.POST, instance=contributor, book=book)

        if form.is_valid():
            form_contributor = form.save(commit=False)
            form_contributor.book = book
            form_contributor.save()

            return redirect(reverse('books_edit_book', kwargs={'book_id': book.pk}))

    template = 'books/edit_contributor.html'
    context = {
        'book': book,
        'contributor': contributor,
        'form': form,
    }

    return render(request, template, context)


@staff_member_required
def edit_format(request, book_id, format_id=None):

    book_format = None
    book = get_object_or_404(models.Book, pk=book_id)

    if format_id:
        book_format = get_object_or_404(models.Format, pk=format_id, book=book)

    form = forms.FormatForm(instance=book_format)

    if request.POST:
        form = forms.FormatForm(request.POST, request.FILES, instance=book_format)
        if form.is_valid():
            form_format = form.save(commit=False)
            form_format.book = book
            form_format.save()

            return redirect(reverse('books_edit_book', kwargs={'book_id': book.pk}))

    template = 'books/edit_format.html'
    context = {
        'book': book,
        'format': book_format,
        'form': form,
    }

    return render(request, template, context)


@staff_member_required
def export_onix_xml(request, book_id=None):

    books = models.Book.objects.all()
    print(books)

    if book_id:
        books = models.Book.objects.filter(pk=book_id)

    template = 'books/onix.xml'
    context = {
        'books': books,
    }

    return render(request, template, context)