# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-08 17:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('standards_review', '0028_auto_20160208_1714'),
    ]

    operations = [
        migrations.RenameField(
            model_name='standard',
            old_name='standard',
            new_name='molecule',
        ),
    ]