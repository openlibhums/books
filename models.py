import uuid
import os
from mimetypes import guess_type

from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.images import get_image_dimensions


fs = FileSystemStorage(location=settings.MEDIA_ROOT)


def cover_images_upload_path(instance, filename):
    try:
        filename = str(uuid.uuid4()) + '.' + str(filename.split('.')[1])
    except IndexError:
        filename = str(uuid.uuid4())

    path = "cover_images/"
    return os.path.join(path, filename)


class Book(models.Model):
    prefix = models.CharField(max_length=20, blank=True, null=True)
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField()
    pages = models.PositiveIntegerField()

    is_edited_volume = models.BooleanField(default=False)
    date_published = models.DateField(blank=True, null=True)

    publisher_name = models.CharField(max_length=100)
    publisher_loc = models.CharField(max_length=100, verbose_name='Publisher location')
    cover = models.FileField(upload_to=cover_images_upload_path, null=True, blank=True, storage=fs)

    doi = models.CharField(max_length=200, blank=True, null=True, verbose_name='DOI', help_text='10.xxx/1234')
    isbn = models.CharField(max_length=30, blank=True, null=True, verbose_name='ISBN')

    purchase_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title

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


class Format(models.Model):
    book = models.ForeignKey(Book)

    title = models.CharField(max_length=100)
    filename = models.CharField(max_length=100)
    sequence = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ('sequence',)

    def __str__(self):
        return self.title
