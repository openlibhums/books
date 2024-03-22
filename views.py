import csv
import magic

from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import Http404
from django.db.models import Q

from plugins.books import models, forms, files, logic
from core import files as core_files


def index(request, category_slug=None):
    category = None
    books = models.Book.objects.filter(
        date_published__isnull=False,
    ).order_by(
        '-date_published',
    )

    if category_slug:
        category = get_object_or_404(
            models.Category,
            slug=category_slug,
        )
        books = books.filter(category=category)

    search = request.GET.get('search')
    if search:
        books = books.filter(
            (Q(title__icontains=search) | Q(description__icontains=search))
        )

    template = 'books/{}/index.html'.format(request.press.theme)
    context = {
        'books': books,
        'category': category,
        'book_settings': models.BookSetting.objects.first(),
    }

    return render(request, template, context)


def view_book(request, book_id):
    book = get_object_or_404(
        models.Book,
        pk=book_id,
        date_published__isnull=False,
    )

    template = 'books/{}/book.html'.format(request.press.theme)
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
    # Forcing a session to be created where people link directly to the book.
    request.session.save()

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


def download_chapter(request, book_id, chapter_id, mark_download='yes'):
    # Forcing a session to be created where people link directly to the book.
    request.session.save()

    book = get_object_or_404(
        models.Book,
        pk=book_id,
        date_published__isnull=False,
    )
    chapter = get_object_or_404(
        models.Chapter,
        pk=chapter_id,
        book=book,
    )

    if mark_download == 'yes':
        chapter.add_book_access(request, 'download')

    # Handle serving the file here
    return files.server_chapter_file(chapter)


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


@staff_member_required
def book_metrics(request):
    """
    Fetches a list of books and displays their metrics between two dates.
    :param request: HttpRequest
    :return: HttpResponse
    """
    start_date, end_date = logic.get_start_and_end_date(request)
    date_form = forms.DateForm(
        initial={'start_date': start_date, 'end_date': end_date}
    )

    books = models.Book.objects.filter(date_published__isnull=False)

    data = logic.book_metrics_data(books, start_date, end_date)

    template = 'books/metrics.html'
    context = {
        'books': books,
        'data': data,
        'date_form': date_form,
    }

    return render(request, template, context)


@staff_member_required
def book_metrics_by_month(request):
    """
    Fetches a list of books and displays their usage by month.
    :param request: HttpRequest
    :return: HttpResponse
    """
    start_month, end_month, date_parts = logic.get_start_and_end_months(request)
    books = models.Book.objects.all()

    month_form = forms.MonthForm(
        initial={
            'start_month': start_month, 'end_month': end_month,
        }
    )

    data, dates, current_year, previous_year = logic.book_metrics_by_month(books, date_parts)

    template = 'books/metrics_by_month.html'
    context = {
        'month_form': month_form,
        'books': books,
        'data': data,
        'dates': dates,
    }

    return render(request, template, context)


@staff_member_required
def books_chapter(request, book_id, chapter_id=None):
    """
    Allows for creation of new or editing of existing chapters.
    :param request: HttpRequest object
    :pram book_id: int Book object pk
    :param chapter_id: optional int Chapter object pk
    :return: HttpResponse or HttpRedirect
    """
    book = get_object_or_404(models.Book, pk=book_id)
    chapter = None
    if chapter_id:
        chapter = get_object_or_404(models.Chapter, pk=chapter_id)

    form = forms.ChapterForm(
        instance=chapter,
        items=logic.get_chapter_contributor_items(book),
        initial={
            'sequence': book.get_next_chapter_sequence() if not chapter else chapter.sequence,
        }
    )

    if request.POST:
        form = forms.ChapterForm(
            request.POST,
            request.FILES,
            instance=chapter,
            items=logic.get_chapter_contributor_items(book),
        )
        form.save(book=book)
        form.save_m2m()
        messages.add_message(
            request,
            messages.SUCCESS,
            'Chapter Saved.',
        )

        return redirect(
            reverse(
                'books_edit_book',
                kwargs={'book_id': book.pk},
            )
        )

    template = 'books/chapter.html'
    context = {
        'form': form,
        'book': book,
        'chapter': chapter,
    }

    return render(request, template, context)


def view_chapter(request, book_id, chapter_id):
    """
    Displays details of a chapter.
    :param request: HttpRequest object
    :param book_id: Book object PK
    :param chapter_id: Chapter object PK
    :return: HttpResponse
    """
    book = get_object_or_404(models.Book, pk=book_id)
    chapter = get_object_or_404(models.Chapter, pk=chapter_id)

    template = 'books/view_chapter.html'
    context = {
        'book': book,
        'chapter': chapter,
    }

    return render(request, template, context)

@staff_member_required
def categories(request, category_id=None):
    """
    Lists all categories.
    """
    all_categories = models.Category.objects.all()
    category, fire_redirect = None, False

    if category_id:
        category = get_object_or_404(
            models.Category,
            pk=category_id,
        )

    form = forms.CategoryForm(instance=category)

    if request.POST:

        if 'delete' in request.POST:
            delete_id = request.POST.get('delete')
            get_object_or_404(
                models.Category,
                pk=delete_id,
            ).delete()
            messages.add_message(
                request,
                messages.ERROR,
                'Category deleted',
            )
            fire_redirect = True

        if 'save' in request.POST:
            form = forms.CategoryForm(
                request.POST,
                instance=category,
            )

            if form.is_valid():
                form.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Category saved.',
                )
                fire_redirect = True

        if fire_redirect:
            return redirect(
                reverse(
                    'books_categories',
                )
            )


    template = 'books/categories.html'
    context = {
        'categories': all_categories,
        'form': form,
    }

    return render(request, template, context)
