from django.shortcuts import render, get_object_or_404
from plugins.books import models
from django.views.decorators.http import require_POST

from pprint import pprint

@require_POST
def move_preprint(request, book_id, book_preprint_id, direction):
    book = get_object_or_404(models.Book, pk=book_id)
    book_preprint = get_object_or_404(models.BookPreprint, id=book_preprint_id, book=book)
    current_order = book_preprint.order

    if direction == 'up':
        # Move up: find the previous item and swap orders
        previous_item = models.BookPreprint.objects.filter(
            book=book,
            order=current_order - 1,
        ).first()
        if previous_item:
            previous_item.order += 1
            previous_item.save()
            book_preprint.order -= 1
            book_preprint.save()

    elif direction == 'down':
        # Move down: find the next item and swap orders
        next_item = models.BookPreprint.objects.filter(
            book=book,
            order=current_order + 1,
        ).first()
        if next_item:
            next_item.order -= 1
            next_item.save()
            book_preprint.order += 1
            book_preprint.save()

    # Fetch the updated list of linked preprints
    linked_preprints = models.BookPreprint.objects.filter(book=book).order_by('order')
    return render(
        request,
        'books/partials/linked_preprints.html',
        {'book': book, 'linked_preprints': linked_preprints},
    )


@require_POST
def remove_preprint(request, book_id, book_preprint_id):
    # Fetch the book and the BookPreprint instance
    book = get_object_or_404(models.Book, pk=book_id)
    book_preprint = get_object_or_404(
        models.BookPreprint,
        id=book_preprint_id,
        book=book,
    )

    # Remove the link between the book and the preprint
    book_preprint.delete()

    # Fetch the updated list of linked preprints
    linked_preprints = models.BookPreprint.objects.filter(
        book=book
    ).order_by('order')

    template = 'books/partials/linked_preprints.html'
    context = {
        'book': book,
        'linked_preprints': linked_preprints,
    }
    return render(
        request,
        template,
        context,
    )