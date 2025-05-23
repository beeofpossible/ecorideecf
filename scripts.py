import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # Remplace par le nom de ton projet
import django
django.setup()

from apps.models import Voyage
from django.utils import timezone
import random

def generer_voyages_ecologiques():
    voyages = Voyage.objects.all()
    
    for voyage in voyages:
        # Ne pas dupliquer si un voyage écologique similaire existe déjà
        exists = Voyage.objects.filter(
            conducteur=voyage.conducteur,
            depart=voyage.depart,
            arrivee=voyage.arrivee,
            date_depart__gt=timezone.now(),
            ecologique=True
        ).exists()
        
        if not exists:
            new_date = voyage.date_depart + timezone.timedelta(days=random.randint(7, 30))
            Voyage.objects.create(
                conducteur=voyage.conducteur,
                titre=f"{voyage.titre} (version écologique)",
                description=voyage.description + " (Ce voyage est écologique)",
                depart=voyage.depart,
                arrivee=voyage.arrivee,
                date_depart=new_date,
                places_disponibles=voyage.places_disponibles,
                prix=voyage.prix,
                ecologique=True,
                etat='A_VENIR'
            )
            print(f"Voyage écologique créé basé sur le voyage {voyage.id}")
        else:
            print(f"Voyage écologique similaire déjà existant pour {voyage.id}")

# Appel de la fonction
generer_voyages_ecologiques()
