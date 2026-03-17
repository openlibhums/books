from django.db import migrations, models
import django.db.models.deletion


def migrate_chapter_filename(apps, schema_editor):
    Chapter = apps.get_model('books', 'Chapter')
    ChapterFormat = apps.get_model('books', 'ChapterFormat')
    for chapter in Chapter.objects.exclude(filename='').exclude(filename__isnull=True):
        ChapterFormat.objects.create(
            chapter=chapter,
            title='Download',
            filename=chapter.filename,
            sequence=10,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0031_book_categories_m2m'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChapterFormat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('filename', models.CharField(max_length=100)),
                ('sequence', models.PositiveIntegerField(default=10)),
                ('chapter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.chapter')),
            ],
            options={
                'ordering': ('sequence',),
            },
        ),
        migrations.RunPython(migrate_chapter_filename, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='chapter',
            name='filename',
        ),
    ]
