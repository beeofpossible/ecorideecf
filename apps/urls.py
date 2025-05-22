from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = "apps"

urlpatterns = [
    path('', views.index, name='home'),
    path("contact", views.contact, name="contact"),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('messagerie/', views.messagerie_view, name='messagerie'),
    path('covoiturage/', views.liste_voyages, name='liste-voyages'),
    path('covoiturage/<int:voyage_id>', views.reserver_voyage, name='voyages-single'),
    path('covoiturage/créer', views.creer_voyage, name='creer-voyage'), 
    path('acheter-credits/', views.acheter_credits, name='acheter_credits'),
    path('paiement/ajouter/', views.ajouter_moyen_paiement, name='ajouter-moyen-paiement'),
    path("connexion/", views.connexion_view, name="connexion"),
    path('inscription/', views.inscription_view, name='inscription'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),
    path('litige/signal/', views.signaler_litige, name='signaler_litige'),
    path('messagerie/litige/<int:litige_id>/', views.messagerie_view, name='voir_litige'),
    path('get_modeles/', views.get_modeles, name='get_modeles'),
    path('véhicule/ajouter', views.ajouter_voiture, name='ajouter_voiture'),
    path('administrateur/espace/', views.espace_admin, name='espace_admin'),
    path('staff/espace/', views.espace_staff, name='espace_staff'),
    path('administrateur/creer-employe/', views.creer_employe, name='creer_employe'),
    path('administrateur/utilisateur/<int:user_id>/suspendre/', views.suspendre_utilisateur, name='suspendre_utilisateur'),
    path('administrateur/utilisateur/<int:user_id>/reactiver/', views.reactiver_utilisateur, name='reactiver_utilisateur'),
    path('administrateur/avis/', views.avis_liste, name='avis_liste'),
    path('administrateur/avis/<int:avis_id>/valider/', views.valider_avis, name='valider_avis'),
    path('administrateur/avis/<int:avis_id>/supprimer/', views.supprimer_avis, name='supprimer_avis'),
    path('administrateur/pages/', views.gestion_pages, name='gestion_pages'),
    path('administrateur/pages/<int:page_id>/', views.gestion_pages, name='gestion_pages'),    
    path('administrateur/presentation/<int:instance_id>/', views.gestion_presentation_utilisateur, name='gestion_presentation_utilisateur'),
    path('administrateur/presentation/', views.gestion_presentation_utilisateur, name='gestion_presentation_utilisateur'),
    path('administrateur/temoignage/', views.gestion_temoignage, name='gestion_temoignage'),
    path('administrateur/temoignage/<int:instance_id>/', views.gestion_temoignage, name='gestion_temoignage'),
    path('administrateur/factures/', views.liste_factures, name='liste_factures'),
    path('administrateur/factures/<int:facture_id>/', views.detail_facture, name='detail_facture'),
    path('presentation-utilisateur/<int:pk>/json/', views.presentation_utilisateur_json, name='presentation_utilisateur_json'),
]
