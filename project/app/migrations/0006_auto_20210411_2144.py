# Generated by Django 3.1.7 on 2021-04-11 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20210411_1046'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallery',
            name='title',
        ),
        migrations.AlterField(
            model_name='gallery',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.DeleteModel(
            name='GalleryImage',
        ),
    ]
