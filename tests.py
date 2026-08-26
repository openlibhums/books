from datetime import datetime, timezone as dt_timezone
from importlib import reload

from django.test import TestCase
from django.urls import clear_url_caches, reverse

import core.urls
from core import include_urls
from utils.testing import helpers

from plugins.books import forms, logic, models, plugin_settings


def mount_plugin_urls():
    # The URLconf is imported before the test database holds the plugin
    # row, so plugin URLs are not mounted. Reload include_urls now the
    # row exists, and core.urls too: its include() holds a nested
    # URLResolver whose url_patterns is a cached_property.
    plugin_settings.install()
    reload(include_urls)
    reload(core.urls)
    clear_url_caches()


class BookMetricsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        mount_plugin_urls()
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
        cls.empty_chapter = models.Chapter.objects.create(
            book=cls.book,
            title='Empty Chapter',
            description='A chapter with no contributors.',
            sequence=1,
        )
        cls.chapter = models.Chapter.objects.create(
            book=cls.book,
            title='Test Chapter',
            description='A chapter for citation tests.',
            sequence=2,
        )
        cls.contributors = [
            models.Contributor.objects.create(
                first_name=first_name,
                last_name=last_name,
                affiliation='Test University',
            )
            for first_name, last_name in [
                ('Ada', 'Lovelace'), ('Charles', 'Babbage'), ('Alan', 'Turing'),
            ]
        ]
        for order, contributor in enumerate(cls.contributors, start=1):
            models.ContributorLink.objects.create(
                contributor=contributor,
                chapter=cls.chapter,
                order=order,
            )

    def test_chapter_citation_with_no_contributors(self):
        self.assertEqual(self.empty_chapter.contributors_citation(), '')

    def test_chapter_citation_uses_citation_name_for_et_al(self):
        self.assertEqual(
            self.chapter.contributors_citation(),
            'Lovelace A. et al. ',
        )


class ChapterContributorTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        mount_plugin_urls()
        cls.press = helpers.create_press()
        cls.staff_user = helpers.create_user(
            'staff@example.com',
            is_staff=True,
            is_active=True,
        )
        cls.book = models.Book.objects.create(
            title='Edited Monograph',
            publisher_name='Test Publisher',
            publisher_loc='Test Location',
        )
        cls.chapter = models.Chapter.objects.create(
            book=cls.book,
            title='Test Chapter',
            description='A chapter for contributor tests.',
            sequence=1,
        )
        cls.book_editor = models.Contributor.objects.create(
            first_name='Book',
            last_name='Editor',
        )
        models.ContributorLink.objects.create(
            contributor=cls.book_editor,
            book=cls.book,
            order=1,
        )
        cls.chapter_author = models.Contributor.objects.create(
            first_name='Chapter',
            last_name='Author',
        )
        models.ContributorLink.objects.create(
            contributor=cls.chapter_author,
            chapter=cls.chapter,
            order=1,
        )
        cls.shared_contributor = models.Contributor.objects.create(
            first_name='Shared',
            last_name='Contributor',
        )
        models.ContributorLink.objects.create(
            contributor=cls.shared_contributor,
            book=cls.book,
            order=2,
        )
        models.ContributorLink.objects.create(
            contributor=cls.shared_contributor,
            chapter=cls.chapter,
            order=2,
        )

    def test_contributor_pool_includes_chapter_only_contributors(self):
        items = logic.get_chapter_contributor_items(self.book)
        contributors = [
            item['object'] for item in items if item['object']
        ]
        self.assertIn(self.book_editor, contributors)
        self.assertIn(self.chapter_author, contributors)

    def test_chapter_form_accepts_chapter_only_contributor(self):
        form = forms.ChapterForm(
            instance=self.chapter,
            items=logic.get_chapter_contributor_items(self.book),
        )
        self.assertIn(
            self.chapter_author,
            form.fields['contributors'].queryset,
        )

    def test_new_chapter_contributor_links_to_chapter_only(self):
        self.client.force_login(self.staff_user)
        url = reverse(
            'books_new_chapter_contributor',
            kwargs={'book_id': self.book.pk, 'chapter_id': self.chapter.pk},
        )
        response = self.client.post(
            url,
            {'first_name': 'New', 'last_name': 'Author'},
            SERVER_NAME=self.press.domain,
        )
        self.assertRedirects(
            response,
            reverse(
                'books_edit_chapter',
                kwargs={
                    'book_id': self.book.pk,
                    'chapter_id': self.chapter.pk,
                },
            ),
        )
        contributor = models.Contributor.objects.get(
            first_name='New',
            last_name='Author',
        )
        self.assertTrue(
            models.ContributorLink.objects.filter(
                contributor=contributor,
                chapter=self.chapter,
            ).exists()
        )
        self.assertFalse(
            models.ContributorLink.objects.filter(
                contributor=contributor,
                book=self.book,
            ).exists()
        )

    def test_removing_book_contributor_keeps_chapter_credit(self):
        self.client.force_login(self.staff_user)
        url = reverse(
            'books_edit_contributor',
            kwargs={
                'book_id': self.book.pk,
                'contributor_id': self.shared_contributor.pk,
            },
        )
        self.client.post(
            url,
            {'delete': self.shared_contributor.pk},
            SERVER_NAME=self.press.domain,
        )
        self.assertTrue(
            models.Contributor.objects.filter(
                pk=self.shared_contributor.pk,
            ).exists()
        )
        self.assertFalse(
            models.ContributorLink.objects.filter(
                contributor=self.shared_contributor,
                book=self.book,
            ).exists()
        )
        self.assertTrue(
            models.ContributorLink.objects.filter(
                contributor=self.shared_contributor,
                chapter=self.chapter,
            ).exists()
        )

    def test_removing_last_link_deletes_contributor(self):
        self.client.force_login(self.staff_user)
        contributor = models.Contributor.objects.create(
            first_name='Sole',
            last_name='Author',
        )
        models.ContributorLink.objects.create(
            contributor=contributor,
            chapter=self.chapter,
            order=3,
        )
        url = reverse(
            'books_edit_chapter_contributor',
            kwargs={
                'book_id': self.book.pk,
                'chapter_id': self.chapter.pk,
                'contributor_id': contributor.pk,
            },
        )
        self.client.post(
            url,
            {'delete': contributor.pk},
            SERVER_NAME=self.press.domain,
        )
        self.assertFalse(
            models.Contributor.objects.filter(pk=contributor.pk).exists()
        )


class PeerReviewDisplayTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        mount_plugin_urls()
        cls.press = helpers.create_press()
        cls.book = models.Book.objects.create(
            title='Reviewed Book',
            publisher_name='Test Publisher',
            publisher_loc='Test Location',
            date_published='2025-01-01',
            peer_reviewed=True,
        )
        cls.url = reverse('books_book', kwargs={'book_id': cls.book.pk})

    def test_book_settings_created_automatically(self):
        models.BookSetting.objects.all().delete()
        self.client.get(self.url, SERVER_NAME=self.press.domain)
        self.assertTrue(models.BookSetting.objects.exists())

    def test_peer_review_status_shown_when_setting_enabled(self):
        book_settings = logic.get_book_settings()
        book_settings.display_review_status = True
        book_settings.save()
        response = self.client.get(self.url, SERVER_NAME=self.press.domain)
        self.assertContains(response, 'Peer Reviewed')

    def test_peer_review_status_hidden_when_setting_disabled(self):
        book_settings = logic.get_book_settings()
        book_settings.display_review_status = False
        book_settings.save()
        response = self.client.get(self.url, SERVER_NAME=self.press.domain)
        self.assertNotContains(response, 'Peer Reviewed')
