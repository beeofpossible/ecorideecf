# Generated by Django 5.2.1 on 2025-05-19 01:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0008_page_presentationutilisateur_temoignage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='presentation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apps.presentationutilisateur'),
        ),
        migrations.AddField(
            model_name='page',
            name='temoignage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='apps.temoignage'),
        ),
    ]
