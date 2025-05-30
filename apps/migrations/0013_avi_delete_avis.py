# Generated by Django 5.2.1 on 2025-05-22 15:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0012_profilutilisateur_photo_profil_url'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Avi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('commentaire', models.TextField(blank=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('est_affiche', models.BooleanField(default=False, help_text='Afficher cet avis publiquement')),
                ('auteur', models.ForeignKey(default='user5', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('voyage', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='avis', to='apps.voyage')),
            ],
            options={
                'unique_together': {('voyage', 'auteur')},
            },
        ),
        migrations.DeleteModel(
            name='Avis',
        ),
    ]
