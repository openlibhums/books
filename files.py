import os
from uuid import uuid4
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import StreamingHttpResponse, Http404
from django.utils.text import slugify

from core import files


def delete_book_file(filename):
    full_path = os.path.join(settings.BASE_DIR, 'files', 'press', 'books', filename)
    os.unlink(full_path)


def save_file_to_disk(file_to_save, book_format):

    if book_format.filename:
        delete_book_file(book_format.filename)

    original_filename = str(file_to_save.name)

    filename = str(uuid4()) + str(os.path.splitext(original_filename)[1])
    folder_structure = os.path.join(settings.BASE_DIR, 'files', 'press', 'books')

    files.save_file_to_disk(file_to_save, filename, folder_structure)

    return filename


def serve_book_file(book_format):
    file_path = os.path.join(settings.BASE_DIR, 'files', 'press', 'books', book_format.filename)

    if os.path.isfile(file_path):
        filename, extension = os.path.splitext(book_format.filename)
        response = StreamingHttpResponse(FileWrapper(open(file_path, 'rb'), 8192),
                                         content_type=files.guess_mime(book_format.filename))
        response['Content-Length'] = os.path.getsize(file_path)
        response['Content-Disposition'] = 'attachment; filename="{0}{1}"'.format(slugify(filename), extension)

        return response
    else:
        raise Http404
