# Generated by Django 3.1.7 on 2021-04-15 07:52

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20210413_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='description',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]
