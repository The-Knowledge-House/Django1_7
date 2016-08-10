# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TuTz718', '0002_auto_20160810_1738'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='linkes',
            new_name='likes',
        ),
    ]
