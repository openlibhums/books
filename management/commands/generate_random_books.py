import random
import string
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from faker import Faker
import svgwrite

from plugins.books import models as book_models

fake = Faker()

# Define the SVG cover creation path
COVERS_DIR = os.path.join(settings.MEDIA_ROOT, 'cover_images')


class Command(BaseCommand):
    help = 'Generate a specified number of random Book instances with contributors and chapters.'

    def add_arguments(self, parser):
        parser.add_argument(
            'num_books',
            type=int,
            help='The number of books to generate.',
        )

    def handle(self, *args, **kwargs):
        num_books = kwargs['num_books']
        categories = book_models.Category.objects.all()
        if not categories:
            self.stdout.write(self.style.ERROR(
                "No categories available. Please add categories first."))
            return

        # Ensure the cover images directory exists
        os.makedirs(COVERS_DIR, exist_ok=True)

        books_created = []
        for _ in range(num_books):
            category = random.choice(categories)
            title = fake.sentence(nb_words=3).title()
            subtitle = fake.sentence(nb_words=5).title() if random.choice(
                [True, False]) else None
            publisher_name = fake.company()
            publisher_loc = fake.city()

            # Generate SVG cover
            cover_filename = f"{title.replace(' ', '_')}_{random.randint(1000, 9999)}.svg"
            cover_path = os.path.join(COVERS_DIR, cover_filename)
            self.create_svg_cover(title, cover_path)

            book = book_models.Book.objects.create(
                title=title,
                subtitle=subtitle,
                category=category,
                description=fake.text(max_nb_chars=200),
                pages=random.randint(100, 500),
                is_edited_volume=random.choice([True, False]),
                is_open_access=random.choice([True, False]),
                date_published=fake.date_this_century(),
                publisher_name=publisher_name,
                publisher_loc=publisher_loc,
                doi=f'10.{random.randint(1000, 9999)}/{random.randint(1000000, 9999999)}',
                isbn=''.join(random.choices(string.digits, k=13)),
                purchase_url=fake.url(),
                license_information=fake.sentence(nb_words=10),
                cover=f'cover_images/{cover_filename}',
            )

            # Add random contributors
            num_contributors = random.randint(2, 10)
            self.create_contributors(book, num_contributors)

            # Add random chapters
            num_chapters = random.randint(5, 15)
            self.create_chapters(book, num_chapters)

            books_created.append(book)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(books_created)} books with contributors and chapters.')
        )

    def create_svg_cover(self, title, filepath):
        # Create an SVG drawing with a black background and the title in white
        svg = svgwrite.Drawing(filepath, size=("200px", "300px"))
        svg.add(svg.rect(insert=(0, 0), size=("100%", "100%"), fill="black"))

        # Add title text to the SVG, centered
        svg.add(
            svg.text(
                title,
                insert=("50%", "50%"),
                text_anchor="middle",
                alignment_baseline="middle",
                fill="white",
                font_size="20px",
                font_family="Arial",
            )
        )
        svg.save()

    def create_contributors(self, book, num_contributors):
        for sequence in range(1, num_contributors + 1):
            first_name = fake.first_name()
            last_name = fake.last_name()
            middle_name = fake.first_name() if random.choice(
                [True, False]) else None

            book_models.Contributor.objects.create(
                book=book,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                affiliation=fake.company(),
                email=fake.email(),
                sequence=sequence,
            )

    def create_chapters(self, book, num_chapters):
        for sequence in range(1, num_chapters + 1):
            title = fake.sentence(nb_words=5).title()
            description = fake.text(max_nb_chars=200)
            doi = f'10.{random.randint(1000, 9999)}/{random.randint(100000, 999999)}'
            pages = random.randint(5, 20)

            chapter = book_models.Chapter.objects.create(
                book=book,
                title=title,
                description=description,
                pages=pages,
                doi=doi,
                number=str(sequence),
                date_published=fake.date_this_century(),
                sequence=sequence,
                filename=f"{title.replace(' ', '_')}.pdf",
            )

            # Add contributors to each chapter
            num_contributors = random.randint(1, 3)
            chapter_contributors = book_models.Contributor.objects.filter(
                book=book).order_by('?')[:num_contributors]
            chapter.contributors.add(*chapter_contributors)
