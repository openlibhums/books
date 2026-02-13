from django.db import migrations, models
import django.db.models.deletion

import core.model_utils


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0024_format_display_read_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContributorLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(default=1)),
                ('contributor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.contributor')),
                ('book', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='books.book')),
                ('chapter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='books.chapter')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='book',
            name='contributors',
            field=core.model_utils.M2MOrderedThroughField(
                blank=True,
                through='books.ContributorLink',
                through_fields=('book', 'contributor'),
                to='books.contributor',
            ),
        ),
    ]
