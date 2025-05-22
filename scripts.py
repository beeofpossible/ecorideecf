import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # Remplace par le nom de ton projet
import django
django.setup()

from django.contrib.auth.models import User
from apps.models import ProfilUtilisateur
import random

# Supprimer d'abord les profils associés
ProfilUtilisateur.objects.filter(utilisateur__username__startswith="user_").delete()

# Puis supprimer les utilisateurs eux-mêmes
User.objects.filter(username__startswith="user_").delete()

def create_user(index, est_conducteur=False):
    username = f"user_{index}"
    email = f"user{index}@exemple.com"
    password = "motdepasse123"

    user, created = User.objects.get_or_create(username=username, defaults={
        "email": email,
        "password": password  # Note : get_or_create ne hash pas le mot de passe, cf. remarque ci-dessous
    })

    if created:
        ProfilUtilisateur.objects.create(utilisateur=user, est_conducteur=est_conducteur)
    else:
        if not hasattr(user, 'profilutilisateur'):
            ProfilUtilisateur.objects.create(utilisateur=user, est_conducteur=est_conducteur)
        else:
            print(f"⚠️ Profil déjà existant pour {username}")
    
    return user

# Création des utilisateurs
for i in range(1, 6):  # Conducteurs
    create_user(i, est_conducteur=True)

for i in range(6, 11):  # Utilisateurs simples
    create_user(i, est_conducteur=False)

for i in range(11, 16):  # Mélange
    create_user(i, est_conducteur=random.choice([True, False]))