from plugins.books import models
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta

from django.utils import timezone


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


def get_first_month_year():
    return '{year}-{month}'.format(year=timezone.now().year, month='01')


def get_current_month_year():
    return '{year}-{month}'.format(
        year=timezone.now().year,
        month=timezone.now().strftime('%m'),
    )


def get_start_and_end_months(request):
    start_month = request.GET.get(
        'start_month', get_first_month_year()
    )

    end_month = request.GET.get(
        'end_month', get_current_month_year()
    )

    start_month_m, start_month_y = start_month.split('-')
    end_month_m, end_month_y = end_month.split('-')

    date_parts = {
        'start_month_m': start_month_m,
        'start_month_y': start_month_y,
        'end_month_m': end_month_m,
        'end_month_y': end_month_y,
        'start_unsplit': start_month,
        'end_unsplit': end_month,
    }

    return start_month, end_month, date_parts


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


def book_metrics_by_month(books, date_parts):
    metrics = models.BookAccess.objects.all()

    start_str = '{}-01'.format(date_parts.get('start_unsplit'))
    end_str = '{}-27'.format(date_parts.get('end_unsplit'))

    start = datetime.strptime(start_str, '%Y-%m-%d').date()
    end = datetime.strptime(end_str, '%Y-%m-%d').date()

    current_year = date_parts.get('end_month_y')
    previous_year = str(int(current_year) - 1)

    dates = [start]

    while start < end:
        start += relativedelta(months=1)
        if start < end:
            dates.append(start)

    data = []

    for book in books:
        book_metrics = metrics.filter(book=book)
        book_data = {'book': book, 'all_metrics': book_metrics}

        date_metrics_list = []

        for date in dates:
            date_metrics = book_metrics.filter(
                accessed__month=date.month,
                accessed__year=date.year,
            )
            date_metrics_list.append(date_metrics.count())

        book_data['date_metrics'] = date_metrics_list

        for year in [current_year, previous_year]:
            book_data[year] = book_metrics.filter(
                accessed__year=year,
            ).count()

        data.append(book_data)

    return data, dates, current_year, previous_year


def get_chapter_contributor_items(book):
    contributors = models.Contributor.objects.filter(
        book=book,
    )
    items = list()
    items.append({'object': None, 'cells': ['First Name', 'Last Name', 'Email']})

    for contributor in contributors:
        item = [
            contributor.first_name,
            contributor.last_name,
            contributor.email,
        ]
        items.append({'object': contributor, 'cells': item})

    return items


