from datetime import datetime, timezone as dt_timezone
from importlib import reload

from django.test import TestCase
from django.urls import clear_url_caches, reverse

import core.urls
from core import include_urls
from utils.testing import helpers

from plugins.books import logic, models, plugin_settings


class BookMetricsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        plugin_settings.install()
        # The URLconf is imported before the test database holds the plugin
        # row, so plugin URLs are not mounted. Reload include_urls now the
        # row exists, and core.urls too: its include() holds a nested
        # URLResolver whose url_patterns is a cached_property.
        reload(include_urls)
        reload(core.urls)
        clear_url_caches()
        cls.press = helpers.create_press()
        cls.staff_user = helpers.create_user(
            'staff@example.com',
            is_staff=True,
            is_active=True,
        )
        cls.book = models.Book.objects.create(
            title='Test Book',
            publisher_name='Test Publisher',
            publisher_loc='Test Location',
        )
        access_datetimes = (
            ('download', datetime(2024, 12, 31, 12, 0, tzinfo=dt_timezone.utc)),
            ('download', datetime(2025, 6, 15, 12, 0, tzinfo=dt_timezone.utc)),
            ('view', datetime(2025, 6, 15, 12, 0, tzinfo=dt_timezone.utc)),
            ('download', datetime(2025, 12, 31, 23, 0, tzinfo=dt_timezone.utc)),
        )
        for access_type, accessed in access_datetimes:
            models.BookAccess.objects.create(
                book=cls.book,
                type=access_type,
                accessed=accessed,
                identifier='test-identifier',
            )

    def test_metrics_range_includes_accesses_on_the_end_date(self):
        data = logic.book_metrics_data(
            [self.book],
            '2025-01-01',
            '2025-12-31',
        )
        self.assertEqual(data[0]['downloads'], 2)
        self.assertEqual(data[0]['views'], 1)

    def test_metrics_split_ranges_sum_to_the_full_range(self):
        early = logic.book_metrics_data(
            [self.book], '2024-01-01', '2024-12-31',
        )
        late = logic.book_metrics_data(
            [self.book], '2025-01-01', '2025-12-31',
        )
        full = logic.book_metrics_data(
            [self.book], '2024-01-01', '2025-12-31',
        )
        self.assertEqual(
            early[0]['downloads'] + late[0]['downloads'],
            full[0]['downloads'],
        )

    def test_metrics_by_month_export_serves_csv(self):
        self.client.force_login(self.staff_user)
        url = reverse('books_metrics_by_month')
        response = self.client.post(
            '{}?start_month=2025-01&end_month=2025-12'.format(url),
            SERVER_NAME=self.press.domain,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
        lines = response.content.decode('utf-8').splitlines()
        self.assertEqual(
            lines[0].split(',')[:2],
            ['Book', 'Book ID'],
        )
        self.assertIn('Jan 2025', lines[0])
        self.assertIn('Dec 2025', lines[0])
        expected_counts = ['0'] * 12
        expected_counts[5] = '2'
        expected_counts[11] = '1'
        self.assertIn(
            ','.join(['Test Book', str(self.book.pk)] + expected_counts),
            lines,
        )

    def test_metrics_by_month_export_requires_staff(self):
        response = self.client.post(
            reverse('books_metrics_by_month'),
            SERVER_NAME=self.press.domain,
        )
        self.assertEqual(response.status_code, 302)


class ChapterCitationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = models.Book.objects.create(
            title='Test Book',
            publisher_name='Test Publisher',
            publisher_loc='Test Location',
        )
        cls.chapter = models.Chapter.objects.create(
            book=cls.book,
            title='Test Chapter',
            description='A chapter for citation tests.',
            sequence=1,
        )
        cls.contributors = [
            models.Contributor.objects.create(
                book=cls.book,
                first_name=first_name,
                last_name=last_name,
                affiliation='Test University',
                sequence=sequence,
            )
            for sequence, (first_name, last_name) in enumerate(
                [('Ada', 'Lovelace'), ('Charles', 'Babbage'), ('Alan', 'Turing')]
            )
        ]

    def test_chapter_citation_with_no_contributors(self):
        self.assertEqual(self.chapter.contributors_citation(), '')

    def test_chapter_citation_uses_citation_name_for_et_al(self):
        self.chapter.contributors.set(self.contributors)
        self.assertEqual(
            self.chapter.contributors_citation(),
            'Lovelace A. et al. ',
        )
