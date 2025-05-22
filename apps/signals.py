from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Credit, ProfilUtilisateur, Facture, Voiture
from django.dispatch import receiver
from django.dispatch import Signal

# Signal personnalisé
credit_achete = Signal()
from .signals import credit_achete

def ajouter(self, montant, achat=False):
    self.montant += montant
    self.save()
    
    if achat:
        credit_achete.send(sender=self.__class__, utilisateur=self.utilisateur, montant=montant)
        
@receiver(post_save, sender=User)
def creer_profil_et_credit_utilisateur(sender, instance, created, **kwargs):
    if created:
        ProfilUtilisateur.objects.create(utilisateur=instance)
        Credit.objects.create(utilisateur=instance, montant=20)

@receiver(credit_achete)
def creer_facture_credit(sender, utilisateur, montant, **kwargs):
    voiture_systeme = Voiture.objects.filter(marque="SYSTEME", modele="CREDITS").first()

    Facture.objects.create(
        voiture=voiture_systeme,
        voyage=None,
        type_facture='achat_credit',
        description=f"Achat de {montant} crédits par {utilisateur.username}",
        montant=montant,
    )