from plugins.books import models
from datetime import date, timedelta


def get_first_day(dt, d_years=0, d_months=0):
    # d_years, d_months are "deltas" to apply to dt
    y, m = dt.year + d_years, dt.month + d_months
    a, m = divmod(m - 1, 12)
    return date(y+a, m + 1, 1)


def get_last_day(dt):
    return get_first_day(dt, 0, 1) + timedelta(-1)


def get_start_and_end_date(request):
    d = date.today()
    start_date = request.GET.get('start_date', get_first_day(d))
    last_date = request.GET.get('end_date', get_last_day(d))

    return start_date, last_date


def book_metrics_data(books, start_date, end_date):

    all_book_data = []

    for book in books:
        book_data = {}
        book_accesses = models.BookAccess.objects.filter(
            book=book,
        )

        views = book_accesses.filter(
            type='view',
            accessed__gte=start_date,
            accessed__lte=end_date,
        )
        downloads = book_accesses.filter(
            type='download',
            accessed__gte=start_date,
            accessed__lte=end_date,
        )

        book_data['book'] = book
        book_data['views'] = views.count()
        book_data['downloads'] = downloads.count()
        book_data['formats'] = []

        for format in book.format_set.all():
            views = views.filter(
                format=format,
            )
            downloads = downloads.filter(
                format=format,
            )
            book_data['formats'].append(
                {
                    'format': format,
                    'views': views.count(),
                    'downloads': downloads.count(),
                }
            )

        all_book_data.append(book_data)

    return all_book_data


