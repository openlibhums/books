import csv
import magic

from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import Http404

from plugins.books import models, forms, files
from core import files as core_files


def index(request):
    books = models.Book.objects.filter(
        date_published__isnull=False,
    ).order_by(
        '-date_published',
    )

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


def download_format(request, book_id, format_id, mark_download='yes'):
    # Forcing a session to be created where people link directly to the book.
    request.session.save()

    book = get_object_or_404(models.Book, pk=book_id, date_published__isnull=False)
    format = get_object_or_404(models.Format, pk=format_id, book=book)

    if mark_download == 'yes':
        format.add_book_access(request, 'download')

    # Handle serving the file here
    return files.serve_book_file(format)


def read_epub(request, book_id, format_id):
    book = get_object_or_404(models.Book, pk=book_id)
    format = get_object_or_404(models.Format, pk=format_id, book=book)

    mime = magic.from_file(files.get_file_path(format), mime=True)

    if not mime == 'application/epub+zip':
        raise Http404

    format.add_book_access(request, 'view')

    template = 'books/book_epub.html'
    context = {
        'book': book,
        'format': format,
    }

    return render(request, template, context)



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
def import_books_upload(request):
    """
    Presents an interface for a CSV file of book metadata to be uploaded for processing.
    :param request: HttpRequest object
    :return: HttpResponse or HttpRedirect on Post
    """
    if request.GET.get('download') == 'true':
        # Generates a sample CSV and serves it.
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(files.CSV_HEADERS)
        writer.writerow(files.CSV_EXAMPLE)
        response['Content-Disposition'] = 'attachment; filename="janeway_book_import_example.csv"'
        return response

    if request.POST and request.FILES:
        temp_file = core_files.save_file_to_temp(request.FILES.get('import'))
        return redirect(reverse('books_import_preview', kwargs={'uuid': temp_file[0].split('.')[0]}))
    elif request.POST and not request.FILES:
        messages.add_message(request, messages.INFO, 'No file provided')

    template = 'books/import_books_upload.html'
    context = {}

    return render(request, template, context)


@staff_member_required
def import_books_preview(request, uuid):
    uuid_csv = '{uuid}.csv'.format(uuid=uuid)
    try:
        has_error, error_message, has_error_lines, error_lines, good_lines = files.verify_upload(uuid_csv)
    except Exception as e:
        has_error = True
        error_message = ['There was a general error processing the uploaded file: {0}.'.format(e)]

    if has_error:
        return render(request, 'books/import_has_error.html', {'error_message': error_message})

    return render(request, 'books/import_verify.html', {'headers': files.CSV_HEADERS,
                                                        'good_rows': good_lines,
                                                        'has_error_lines': has_error_lines,
                                                        'error_lines:': error_lines,
                                                        'UUID': uuid})


@staff_member_required
def import_books_process(request, uuid):
    uuid = '{uuid}.csv'.format(uuid=uuid)

    if request.POST:
        files.perform_book_import(uuid)
        return redirect(reverse('books_admin'))
    else:
        messages.add_message(request, messages.INFO, 'Post required')
        return redirect(reverse('books_import_preview', kwargs={'uuid': uuid}))


@staff_member_required
def export_onix_xml(request, book_id=None):
    books = models.Book.objects.all()

    if book_id:
        books = models.Book.objects.filter(pk=book_id)

    template = 'books/onix.xml'
    context = {
        'books': books,
    }

    return render(request, template, context)
