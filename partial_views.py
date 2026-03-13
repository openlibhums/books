from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST, require_GET

from plugins.books import models, logic


@require_GET
@staff_member_required
def contributor_name_fields(request):
    is_corporate = request.GET.get('is_corporate') == 'on'
    return render(
        request,
        'books/partials/contributor_name_fields.html',
        {'is_corporate': is_corporate},
    )


@require_POST
@staff_member_required
def move_preprint(request, book_id, book_preprint_id, direction):
    book = get_object_or_404(models.Book, pk=book_id)
    book_preprint = get_object_or_404(
        models.BookPreprint, id=book_preprint_id, book=book,
    )
    queryset = models.BookPreprint.objects.filter(book=book).order_by('order')
    logic.swap_order(book_preprint, direction, queryset)

    linked_preprints = models.BookPreprint.objects.filter(
        book=book,
    ).order_by('order')
    return render(
        request,
        'books/partials/linked_preprints.html',
        {'book': book, 'linked_preprints': linked_preprints},
    )


@require_POST
@staff_member_required
def remove_preprint(request, book_id, book_preprint_id):
    book = get_object_or_404(models.Book, pk=book_id)
    book_preprint = get_object_or_404(
        models.BookPreprint,
        id=book_preprint_id,
        book=book,
    )

    book_preprint.delete()

    linked_preprints = models.BookPreprint.objects.filter(
        book=book
    ).order_by('order')

    return render(
        request,
        'books/partials/linked_preprints.html',
        {'book': book, 'linked_preprints': linked_preprints},
    )


@require_POST
@staff_member_required
def move_book_contributor(request, book_id, contributor_link_id, direction):
    book = get_object_or_404(models.Book, pk=book_id)
    link = get_object_or_404(
        models.ContributorLink, id=contributor_link_id, book=book,
    )
    queryset = models.ContributorLink.objects.filter(
        book=book,
    ).order_by('order')
    logic.swap_order(link, direction, queryset)

    contributor_links = models.ContributorLink.objects.filter(
        book=book,
    ).order_by('order')
    response = render(
        request,
        'books/partials/book_contributors.html',
        {'book': book, 'contributor_links': contributor_links},
    )
    response['HX-Trigger-After-Swap'] = logic.trigger_message(
        link.contributor, direction,
    )
    return response


@require_POST
@staff_member_required
def move_chapter_contributor(
    request, book_id, chapter_id, contributor_link_id, direction,
):
    book = get_object_or_404(models.Book, pk=book_id)
    chapter = get_object_or_404(models.Chapter, pk=chapter_id, book=book)
    link = get_object_or_404(
        models.ContributorLink, id=contributor_link_id, chapter=chapter,
    )
    queryset = models.ContributorLink.objects.filter(
        chapter=chapter,
    ).order_by('order')
    logic.swap_order(link, direction, queryset)

    contributor_links = models.ContributorLink.objects.filter(
        chapter=chapter,
    ).order_by('order')
    response = render(
        request,
        'books/partials/chapter_contributors.html',
        {'book': book, 'chapter': chapter, 'contributor_links': contributor_links},
    )
    response['HX-Trigger-After-Swap'] = logic.trigger_message(
        link.contributor, direction,
    )
    return response


@require_POST
@staff_member_required
def move_format(request, book_id, format_id, direction):
    book = get_object_or_404(models.Book, pk=book_id)
    book_format = get_object_or_404(models.Format, pk=format_id, book=book)
    queryset = models.Format.objects.filter(book=book).order_by('sequence')
    logic.swap_order(book_format, direction, queryset, order_field='sequence')

    formats = models.Format.objects.filter(book=book).order_by('sequence')
    response = render(
        request,
        'books/partials/book_formats.html',
        {'book': book, 'formats': formats},
    )
    response['HX-Trigger-After-Swap'] = logic.trigger_message(
        book_format.title, direction,
    )
    return response


@require_POST
@staff_member_required
def move_chapter(request, book_id, chapter_id, direction):
    book = get_object_or_404(models.Book, pk=book_id)
    chapter = get_object_or_404(models.Chapter, pk=chapter_id, book=book)
    queryset = models.Chapter.objects.filter(book=book).order_by('sequence')
    logic.swap_order(chapter, direction, queryset, order_field='sequence')

    chapters = models.Chapter.objects.filter(book=book).order_by('sequence')
    response = render(
        request,
        'books/partials/book_chapters.html',
        {'book': book, 'chapters': chapters},
    )
    response['HX-Trigger-After-Swap'] = logic.trigger_message(
        chapter.title, direction,
    )
    return response
