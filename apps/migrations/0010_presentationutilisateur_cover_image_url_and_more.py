# Generated by Django 5.2.1 on 2025-05-21 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0009_page_presentation_page_temoignage'),
    ]

    operations = [
        migrations.AddField(
            model_name='presentationutilisateur',
            name='cover_image_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='presentationutilisateur',
            name='miniature_image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
