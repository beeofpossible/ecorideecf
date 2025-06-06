# Generated by Django 5.2.1 on 2025-05-11 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='site',
            name='cover_image_url',
            field=models.URLField(blank=True, null=True, verbose_name="URL de l'image de couverture"),
        ),
    ]
