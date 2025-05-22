from django.db import models
from django.contrib.auth.models import User


# Modèle pour l'utilisateur (hérite de User)
class ProfilUtilisateur(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE)
    est_conducteur = models.BooleanField(default=False)  # Permet de savoir si l'utilisateur est conducteur
    bio = models.TextField(blank=True, null=True)
    photo_profil = models.ImageField(upload_to='photos_profil/', null=True, blank=True)
    photo_profil_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.utilisateur.username

class Site(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    cover_image = models.ImageField(upload_to="", null=True, blank=True)  # Ajout de la cover image
    cover_image_url = models.URLField("URL de l'image de couverture", blank=True, null=True)  # Ajout de l'URL
    cover_text = models.CharField("cover text", max_length=200, default="test")
    # Avantages
    avantage_1 = models.CharField("Avantage 1", max_length=200)
    avantage_2 = models.CharField("Avantage 2", max_length=200)
    avantage_3 = models.CharField("Avantage 3", max_length=200)

    # Icônes Font Awesome associées aux avantages
    icone_avantage_1 = models.CharField("Icône Avantage 1", max_length=100, blank=True, null=True)
    icone_avantage_2 = models.CharField("Icône Avantage 2", max_length=100, blank=True, null=True)
    icone_avantage_3 = models.CharField("Icône Avantage 3", max_length=100, blank=True, null=True)
    #Description avantage 3 
    description_avantage_1 = models.CharField("Description Avantage 3", max_length=200, default="test")
    description_avantage_2 = models.CharField("Description Avantage 3", max_length=200, default="test")
    description_avantage_3 = models.CharField("Description Avantage 3", max_length=200, default="test")
    def __str__(self):
        return self.titre

    def get_avantages(self):
        return [
            {"avantage": self.avantage_1, "icone": self.icone_avantage_1, "description": self.description_avantage_1},
            {"avantage": self.avantage_2, "icone": self.icone_avantage_2, "description": self.description_avantage_2},
            {"avantage": self.avantage_3, "icone": self.icone_avantage_3, "description": self.description_avantage_3},
        ]

# Modèle pour un Voyage
class Voyage(models.Model):
    conducteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voyages')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    depart = models.CharField(max_length=100)  # Ville de départ
    arrivee = models.CharField(max_length=100)  # Ville d'arrivée
    date_depart = models.DateTimeField()
    places_disponibles = models.PositiveIntegerField()
    prix = models.DecimalField(max_digits=6, decimal_places=2)  # Prix par passager

    def __str__(self):
        return f"Voyage de {self.conducteur.username} : {self.depart} -> {self.arrivee}"

    def reserver_place(self):
        """Réserve une place pour un passager, en réduisant le nombre de places disponibles."""
        if self.places_disponibles > 0:
            self.places_disponibles -= 1
            self.save()
            return True
        return False

# Modèle pour une Réservation
class Reservation(models.Model):
    voyage = models.ForeignKey(Voyage, on_delete=models.CASCADE, related_name='reservations')
    passager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    date_reservation = models.DateTimeField(auto_now_add=True)
    montant = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.passager.username} a réservé une place sur le voyage de {self.voyage.conducteur.username}."

class Message(models.Model):
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_envoyes")
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_recus")
    contenu = models.TextField()
    date_envoye = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.expediteur.username} → {self.destinataire.username} ({self.date_envoye})"
class MoyenPaiement(models.Model):
    TYPE_CHOICES = [
        ('CB', 'Carte Bancaire'),
        ('PAYPAL', 'PayPal'),
        ('STRIPE', 'Stripe'),
        ('APPLEPAY', 'Apple Pay'),
        ('GOOGLEPAY', 'Google Pay'),
        ('AUTRE', 'Autre'),
    ]

    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moyens_paiement')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    nom = models.CharField(max_length=100, help_text="Nom sur le moyen de paiement (ex : Visa, compte PayPal...)")
    details = models.CharField(max_length=200, blank=True, help_text="Détails (4 derniers chiffres, identifiant PayPal...)")
    actif = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.nom} ({'actif' if self.actif else 'inactif'})"
    
class Litige(models.Model):
    TYPE_CHOICES = [
        ('voyage', 'Voyage'),
        ('reservation', 'Réservation'),
    ]

    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='litiges_envoyes')
    type_litige = models.CharField(max_length=20, choices=TYPE_CHOICES)
    voyage = models.ForeignKey(Voyage, on_delete=models.CASCADE, null=True, blank=True, related_name='litiges')
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, null=True, blank=True, related_name='litiges')
    sujet = models.CharField(max_length=255)
    description_initiale = models.TextField()
    est_resolu = models.BooleanField(default=False)
    date_ouverture = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Litige #{self.id} - {self.sujet} ({'résolu' if self.est_resolu else 'ouvert'})"

    def get_conducteur(self):
        if self.type_litige == 'voyage' and self.voyage:
            return self.voyage.conducteur
        elif self.type_litige == 'reservation' and self.reservation:
            return self.reservation.voyage.conducteur
        return None

class Avi(models.Model):
    voyage = models.ForeignKey('Voyage', on_delete=models.CASCADE, related_name='avis', default=1)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, default="user5") 
    note = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 à 5 étoiles
    commentaire = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    est_affiche = models.BooleanField(default=False, help_text="Afficher cet avis publiquement")

    class Meta:
        unique_together = ('voyage', 'auteur')  # Un seul avis par voyage et par utilisateur

    def __str__(self):
        return f"{self.auteur.username} - {self.note}⭐ sur {self.voyage}"

class Credit(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='credit')
    montant = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.utilisateur.username} : {self.montant} crédits"

    def ajouter(self, montant):
        self.montant += montant
        self.save()

    def retirer(self, montant):
        if self.montant >= montant:
            self.montant -= montant
            self.save()
            return True
        return False

class Voiture(models.Model):
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='voitures')
    marque = models.CharField(max_length=100)
    modele = models.CharField(max_length=100)
    couleur = models.CharField(max_length=50, blank=True, null=True)
    immatriculation = models.CharField(max_length=20, unique=True)
    nombre_places = models.PositiveIntegerField(default=4)
    photo = models.ImageField(upload_to='voitures/', blank=True, null=True) 

    def __str__(self):
        return f"{self.marque} {self.modele} ({self.immatriculation})"

class Facture(models.Model):
    FACTURE_TYPE_CHOICES = [
        ('achat_credit', 'Achat de crédits'),
        ('100€ carburant', "100€ carburant"), 
        ('autre', 'Autre'),
    ]

    voiture = models.ForeignKey(Voiture, on_delete=models.CASCADE, related_name='factures', null=True, blank=True)
    voyage = models.ForeignKey(Voyage, on_delete=models.SET_NULL, null=True, blank=True, related_name='factures')
    type_facture = models.CharField(max_length=20, choices=FACTURE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    montant = models.DecimalField(max_digits=8, decimal_places=2)
    date_facture = models.DateField(auto_now_add=True)
    document = models.FileField(upload_to='factures/', blank=True, null=True)

    def __str__(self):
        label = f"{self.get_type_facture_display()} - {self.montant}€"
        if self.voyage:
            label += f" (Voyage: {self.voyage.titre})"
        return label


class PresentationUtilisateur(models.Model):
    titre = models.CharField(max_length=200)
    sous_titre = models.CharField(max_length=200)
    description_courte = models.CharField(max_length=500)
    cover_image = models.ImageField(upload_to='presentations/', blank=True, null=True)
    cover_image_url = models.URLField(blank=True, null=True)  
    miniature_image = models.ImageField(upload_to='presentations/miniatures/', blank=True, null=True)  # Image miniature
    miniature_image_url = models.URLField(blank=True, null=True) 
   
    # Raisons d'utiliser Ecoride
    raison_1_titre = models.CharField(max_length=200)
    raison_1_description = models.TextField()
    raison_1_icone = models.CharField(max_length=100, blank=True, null=True)
    raison_1_image = models.ImageField(upload_to='presentations/raisons/', blank=True, null=True)

    raison_2_titre = models.CharField(max_length=200)
    raison_2_description = models.TextField()
    raison_2_icone = models.CharField(max_length=100, blank=True, null=True)
    raison_2_image = models.ImageField(upload_to='presentations/raisons/', blank=True, null=True)

    raison_3_titre = models.CharField(max_length=200)
    raison_3_description = models.TextField()
    raison_3_icone = models.CharField(max_length=100, blank=True, null=True)
    raison_3_image = models.ImageField(upload_to='presentations/raisons/', blank=True, null=True)

    def __str__(self):
        return self.titre

class Temoignage(models.Model):
    titre = models.CharField(max_length=200)
    sous_titre = models.CharField(max_length=200)
    cover_image = models.ImageField(upload_to='temoignages/', blank=True, null=True)  # Image de couverture

    # Témoignage 1
    temoignage_1_titre = models.CharField(max_length=200)
    temoignage_1_sous_titre = models.CharField(max_length=200)
    temoignage_1_texte = models.TextField()
    temoignage_1_image = models.ImageField(upload_to='temoignages/', blank=True, null=True)

    # Témoignage 2
    temoignage_2_titre = models.CharField(max_length=200)
    temoignage_2_sous_titre = models.CharField(max_length=200)
    temoignage_2_texte = models.TextField()
    temoignage_2_image = models.ImageField(upload_to='temoignages/', blank=True, null=True)

    # Témoignage 3
    temoignage_3_titre = models.CharField(max_length=200)
    temoignage_3_sous_titre = models.CharField(max_length=200)
    temoignage_3_texte = models.TextField()
    temoignage_3_image = models.ImageField(upload_to='temoignages/', blank=True, null=True)

    def __str__(self):
        return self.titre


class Page(models.Model):
    TYPE_CHOICES = [
        ('utilisateurs', 'Présentation des utilisateurs'),
        ('temoignages', 'Témoignages et avantages'),
    ]
    presentation = models.ForeignKey(PresentationUtilisateur, on_delete=models.SET_NULL, null=True, blank=True)
    temoignage = models.ForeignKey(Temoignage, on_delete=models.SET_NULL, null=True, blank=True)
    titre = models.CharField(max_length=200)
    sous_titre = models.CharField(max_length=200)
    description_courte = models.CharField(max_length=500)
    cover_image = models.ImageField(upload_to='pages/', blank=True, null=True)  # Image de couverture
    type_page = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Sections dynamiques
    section_1_titre = models.CharField(max_length=200)
    section_1_sous_titre = models.CharField(max_length=200)
    section_1_texte = models.TextField()
    section_1_image = models.ImageField(upload_to='pages/sections/', blank=True, null=True)

    section_2_titre = models.CharField(max_length=200)
    section_2_sous_titre = models.CharField(max_length=200)
    section_2_texte = models.TextField()
    section_2_image = models.ImageField(upload_to='pages/sections/', blank=True, null=True)

    section_3_titre = models.CharField(max_length=200)
    section_3_sous_titre = models.CharField(max_length=200)
    section_3_texte = models.TextField()
    section_3_image = models.ImageField(upload_to='pages/sections/', blank=True, null=True)

    def __str__(self):
        return self.titre

