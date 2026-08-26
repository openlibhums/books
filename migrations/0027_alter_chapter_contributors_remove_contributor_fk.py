from django.db import migrations, models

import core.model_utils


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0026_migrate_contributor_data'),
    ]

    operations = [
        # Cannot AlterField on M2M to add through=, so remove and re-add.
        migrations.RemoveField(
            model_name='chapter',
            name='contributors',
        ),
        migrations.AddField(
            model_name='chapter',
            name='contributors',
            field=core.model_utils.M2MOrderedThroughField(
                blank=True,
                through='books.ContributorLink',
                through_fields=('chapter', 'contributor'),
                to='books.contributor',
                related_name='chapter_contributors',
            ),
        ),
        migrations.RemoveField(
            model_name='contributor',
            name='book',
        ),
        migrations.RemoveField(
            model_name='contributor',
            name='sequence',
        ),
        migrations.AlterModelOptions(
            name='contributor',
            options={'ordering': ('last_name', 'first_name')},
        ),
    ]
