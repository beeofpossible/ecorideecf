import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # Remplace par le nom de ton projet
import django
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from apps.home.models import Voyage, Utilisateur
from datetime import datetime, timedelta

class VoyageTestCase(TestCase):
    def setUp(self):
        # Créer un conducteur
        self.conducteur = Utilisateur.objects.create_user(username="testuser", password="password123")
        
        # Créer un voyage
        self.voyage = Voyage.objects.create(
            titre="Test Voyage",
            depart="Paris",
            arrivee="Lyon",
            date_depart=datetime.now() + timedelta(days=1),
            nb_places_restantes=3,
            prix=50.0,
            conducteur=self.conducteur,
            ecologique=True
        )
        self.client = Client()

    def test_voyage_creation(self):
        self.assertEqual(self.voyage.titre, "Test Voyage")
        self.assertTrue(self.voyage.ecologique)
        self.assertEqual(self.voyage.nb_places_restantes, 3)

    def test_liste_voyages_view_status_code(self):
        url = reverse('apps:liste_voyages')  # Ajuste selon ton nom d'URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Voyage")

    def test_filter_depart(self):
        url = reverse('apps:liste_voyages') + "?depart=Paris"
        response = self.client.get(url)
        self.assertContains(response, "Test Voyage")
        url2 = reverse('apps:liste_voyages') + "?depart=Lyon"
        response2 = self.client.get(url2)
        self.assertNotContains(response2, "Test Voyage")
