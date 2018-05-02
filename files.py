import os
from uuid import uuid4
from wsgiref.util import FileWrapper
from csv import DictReader

from django.conf import settings
from django.http import StreamingHttpResponse, Http404
from django.utils.text import slugify

from core import files

CSV_HEADERS = ['Prefix', 'Title', 'Subtitle', 'Description', 'Pages', 'Edited Volume', 'Date Published',
               'Publisher Name', 'Publisher Location', 'DOI', 'ISBN', 'Purchase URL']
CSV_EXAMPLE = ['The', 'Lord of the Rings', 'Fellowship if the Ring', 'Hobbit takes jewellery on excursion', '398',
               '0', '1954-07-29', 'Allen and Unwin', 'London', '10.1234/123.1', '0618346252',
               'https://www.amazon.com/Fellowship-Ring-Being-First-Rings/dp/0547928211/']
temp_directory = os.path.join(settings.BASE_DIR, 'files', 'temp')


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


def pre_process(uuid):
    out_text = ''

    with open(os.path.join(temp_directory, uuid), 'r') as in_file:
        out_text += in_file.readline()

        out_text = out_text.replace(' ,', ',')
        out_text = out_text.replace(', ', ',')
        out_text += in_file.read()

    with open(os.path.join(temp_directory, uuid), 'w') as out_file:
        out_file.write(out_text)


def verify_upload(uuid):
    is_verified = False
    has_error = False
    error_message = []
    has_error_lines = False
    error_lines = []
    good_lines = []

    # remove dud lines
    pre_process(uuid)

    with open(os.path.join(temp_directory, uuid), 'r') as in_file:
        reader = DictReader(in_file)

        counter = 0

        for row in reader:
            counter += 1
            try:
                if not is_verified:
                    for item in CSV_HEADERS:
                        if not item in row:
                            has_error = True
                            error_message.append('Expected field \'{0}\' is not present in the upload on line {1}.'.format(item, counter))
                    is_verified = True

                    if has_error:
                        return has_error, error_message, has_error_lines, error_lines, good_lines

                output_row = []

                for item in CSV_HEADERS:
                    output_row.append(row[item])

                good_lines.append(output_row)
            except:
                error_lines.append(counter)

    return has_error, error_message, has_error_lines, error_lines, good_lines
