from django.db import migrations


def forwards(apps, schema_editor):
    Contributor = apps.get_model('books', 'Contributor')
    ContributorLink = apps.get_model('books', 'ContributorLink')
    Chapter = apps.get_model('books', 'Chapter')

    # Book contributors: copy FK relationship into ContributorLink
    for contributor in Contributor.objects.all():
        ContributorLink.objects.create(
            contributor=contributor,
            book=contributor.book,
            order=contributor.sequence,
        )

    # Chapter contributors: copy old M2M into ContributorLink
    for chapter in Chapter.objects.all():
        for order, contributor in enumerate(
            chapter.contributors.all(), start=1
        ):
            # Use get_or_create to avoid duplicates if a contributor
            # is linked to both a book and a chapter
            ContributorLink.objects.get_or_create(
                contributor=contributor,
                chapter=chapter,
                defaults={'order': order},
            )


def backwards(apps, schema_editor):
    ContributorLink = apps.get_model('books', 'ContributorLink')
    Contributor = apps.get_model('books', 'Contributor')

    # Restore Contributor.book FK from ContributorLink book entries
    for link in ContributorLink.objects.filter(book__isnull=False):
        contributor = link.contributor
        contributor.book = link.book
        contributor.sequence = link.order
        contributor.save()

    # Chapter M2M will be restored automatically when the field
    # is reverted to a plain M2M in the reverse schema migration


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0025_contributorlink_and_book_contributors'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
