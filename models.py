import uuid
import os
from mimetypes import guess_type
from datetime import timedelta
import magic
from urllib.parse import urlparse

from user_agents import parse as parse_ua_string

from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.images import get_image_dimensions
from django.utils import timezone
from django.core.exceptions import ValidationError

from metrics.logic import get_iso_country_code
from utils.shared import get_ip_address
from core import models as core_models
from plugins.books import files
from core.file_system import JanewayFileSystemStorage


fs = JanewayFileSystemStorage()


def cover_images_upload_path(instance, filename):
    try:
        filename = str(uuid.uuid4()) + '.' + str(filename.split('.')[1])
    except IndexError:
        filename = str(uuid.uuid4())

    path = "cover_images/"
    return os.path.join(path, filename)


class BookSetting(models.Model):
    book_page_title = models.CharField(
        max_length=255,
        default="Published Books",
    )

    def save(self, *args, **kwargs):
        if not self.pk and BookSetting.objects.exists():
            raise ValidationError('There is can be only one BookSetting instance')
        return super(BookSetting, self).save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(
        null=True,
        blank=True,
    )
    display_title = models.BooleanField(
        default=True,
        help_text="Mark as false if you want to hide the category title.",
    )
    chapter_name = models.CharField(
        max_length=200,
        default='Chapter',
    )
    chapter_name_plural = models.CharField(
        max_length=200,
        default='Chapters',
    )

    class Meta:
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Book(models.Model):
    prefix = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    description = models.TextField()
    pages = models.PositiveIntegerField()

    is_edited_volume = models.BooleanField(default=False)
    is_open_access = models.BooleanField(default=True)
    date_published = models.DateField(
        blank=True,
        null=True,
    )

    publisher_name = models.CharField(max_length=100)
    publisher_loc = models.CharField(max_length=100, verbose_name='Publisher location')
    cover = models.FileField(upload_to=cover_images_upload_path, null=True, blank=True, storage=fs)

    doi = models.CharField(max_length=200, blank=True, null=True, verbose_name='DOI', help_text='10.xxx/1234')
    isbn = models.CharField(max_length=30, blank=True, null=True, verbose_name='ISBN')

    purchase_url = models.URLField(null=True, blank=True)

    remote_url = models.URLField(
        null=True,
        blank=True,
        help_text='Set this if you want to have your book link out to a remote '
                  'website rather than local formats.'
    )
    remote_label = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Label for the remote link. If left blank will display as '
                  '"View on yourremoteurldomain.com"',
    )

    def __str__(self):
        return self.title

    def citation(self):
        return "{authors} {year}. <em>{title}</em>".format(
            authors=self.contributors_citation(),
            year=self.date_published.year,
            title=self.full_title(),
        )

    def contributors_citation(self):
        contributors = self.contributor_set.all()

        if contributors.count() == 1:
            return '{contributor} '.format(
                contributor=contributors[0].citation_name()
            )
        elif contributors.count() == 2:
            return '{contributor_one} & {contributor_two} '.format(
                contributor_one=contributors[0].citation_name(),
                contributor_two=contributors[1].citation_name(),
            )
        else:
            return '{contributor} et al. '.format(contributor=contributors[0])

    def full_title(self):
        if self.prefix and self.subtitle:
            return "{0} {1}: {2}".format(self.prefix, self.title, self.subtitle)
        elif self.prefix:
            return "{0} {1}".format(self.prefix, self.title)
        elif self.subtitle:
            return "{0}: {1}".format(self.title, self.subtitle)
        else:
            return self.title

    def first_contributor(self):
        contributors = self.contributor_set.all()
        if contributors:
            return contributors[0]
        else:
            return 'No Authors'

    def get_next_contributor_sequence(self):
        if self.contributor_set.all():
            last_contributor = self.contributor_set.all().reverse()[0]
            return last_contributor.sequence + 1
        else:
            return 1

    def get_next_chapter_sequence(self):
        chapter_sequences = [c.sequence for c in self.chapter_set.all()]

        if chapter_sequences:
            return max(chapter_sequences) + 1
        else:
            return 0

    def cover_onix_code(self):
        mapping = {
            'image/gif': 'D501',
            'image/jpeg': 'D502',
            'image/png': 'D503',
            'image/tiff': 'D504'
        }
        return mapping.get(guess_type(self.cover.url)[0], 'D502')

    def cover_height(self):
        width, height = get_image_dimensions(self.cover)
        return height

    def cover_width(self):
        width, height = get_image_dimensions(self.cover)
        return width

    def metrics(self):
        all_metrics = BookAccess.objects.filter(
            book=self,
        )

        views = all_metrics.filter(type='view')
        downloads = all_metrics.filter(type='download')

        return {
            'total': all_metrics.count(),
            'views': views.count(),
            'downloads': downloads.count(),
        }

    def remote_book_label(self):
        if self.remote_label:
            return self.remote_label
        else:
            return 'View on {}'.format(
                urlparse(self.remote_url).netloc
            )


class Contributor(models.Model):
    book = models.ForeignKey(Book)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)

    affiliation = models.TextField()
    email = models.EmailField(blank=True, null=True)
    sequence = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ('sequence',)

    def __str__(self):
        if not self.middle_name:
            return "{0} {1}".format(self.first_name, self.last_name)
        else:
            return "{0} {1} {2}".format(self.first_name, self.middle_name, self.last_name)

    def middle_initial(self):
        if self.middle_name:
            return '{middle_initial}.'.format(middle_initial=self.middle_name[0])

    def citation_name(self):
        return '{last_name} {first_initial}.'.format(
            last_name=self.last_name,
            first_initial=self.first_name[0],
        )


class Format(models.Model):
    book = models.ForeignKey(Book)

    title = models.CharField(max_length=100)
    filename = models.CharField(max_length=100)
    sequence = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ('sequence',)

    def __str__(self):
        return self.title

    def is_epub(self):
        mime = magic.from_file(files.get_file_path(self), mime=True)
        if mime == 'application/epub+zip':
            return True

    def add_book_access(self, request, access_type='download'):
        try:
            user_agent = parse_ua_string(request.META.get('HTTP_USER_AGENT', None))
        except TypeError:
            user_agent = None

        ip = get_ip_address(request)
        iso_country_code = get_iso_country_code(ip)
        identifier = request.session.session_key

        try:
            country = core_models.Country.objects.get(
                code=iso_country_code,
            )
        except core_models.Country.DoesNotExist:
            country = None

        if user_agent and not user_agent.is_bot:

            # check if the current IP has accessed this article recently.
            time_to_check = timezone.now() - timedelta(seconds=10)
            check = BookAccess.objects.filter(
                book=self.book,
                format=self,
                accessed__gte=time_to_check,
                type=access_type,
                identifier=identifier,
            ).count()

            if not check:
                BookAccess.objects.create(
                    book=self.book,
                    format=self,
                    type=access_type,
                    country=country,
                    identifier=identifier,
                )


def access_choices():
    return (
        ('download', 'Download'),  # A download of any book format
        ('view', 'View'),  # A view of a book page
    )


class BookAccess(models.Model):
    book = models.ForeignKey(Book)
    chapter = models.ForeignKey('Chapter', blank=True, null=True)
    type = models.CharField(max_length=20, choices=access_choices())
    format = models.ForeignKey(Format, blank=True, null=True)
    accessed = models.DateTimeField(default=timezone.now)
    country = models.ForeignKey('core.Country', null=True, blank=True)
    identifier = models.CharField(max_length=100)

    def __str__(self):
        return '[{0}] - {1} at {2}'.format(
            self.format,
            self.book.title,
            self.accessed,
        )


class Chapter(models.Model):
    book = models.ForeignKey(Book)
    title = models.CharField(
        max_length=255,
    )
    description = models.TextField()
    pages = models.PositiveIntegerField()
    doi = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='DOI',
        help_text='10.xxx/1234',
    )
    number = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='The chapter number eg. 1',
    )
    sequence = models.PositiveIntegerField(
        help_text='The order in which the chapters should appear.',
    )
    contributors = models.ManyToManyField(
        Contributor,
        null=True,
        related_name='chapter_contributors',
    )
    filename = models.CharField(
        max_length=255,
    )

    class Meta:
        ordering = ('sequence', 'number',)

    def __str__(self):
        return '[{0}] {1} ({2})'.format(
            self.number,
            self.title,
            self.book.title,
        )

    def add_book_access(self, request, access_type='download'):
        try:
            user_agent = parse_ua_string(request.META.get('HTTP_USER_AGENT', None))
        except TypeError:
            user_agent = None

        ip = get_ip_address(request)
        iso_country_code = get_iso_country_code(ip)
        identifier = request.session.session_key

        try:
            country = core_models.Country.objects.get(
                code=iso_country_code,
            )
        except core_models.Country.DoesNotExist:
            country = None

        if user_agent and not user_agent.is_bot:

            # check if the current IP has accessed this article recently.
            time_to_check = timezone.now() - timedelta(seconds=10)
            check = BookAccess.objects.filter(
                book=self.book,
                chapter=self,
                accessed__gte=time_to_check,
                type=access_type,
                identifier=identifier,
            ).count()

            if not check:
                BookAccess.objects.create(
                    book=self.book,
                    chapter=self,
                    type=access_type,
                    country=country,
                    identifier=identifier,
                )
