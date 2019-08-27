# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-30 13:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_auto_20190628_1608'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('pages', models.PositiveIntegerField()),
                ('doi', models.CharField(blank=True, help_text='10.xxx/1234', max_length=200, null=True, verbose_name='DOI')),
                ('number', models.PositiveIntegerField(blank=True, null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.Book')),
                ('contributors', models.ManyToManyField(null=True, to='books.Contributor')),
            ],
        ),
    ]