# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-07-31 11:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0008_chapter_filename'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='sequence',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
