from django.shortcuts import render, get_object_or_404, redirect
from .models import Voyage, Reservation, Site, Page, PresentationUtilisateur, Temoignage
from .models import ProfilUtilisateur, Message, Litige, Avi, Voiture, Facture, Credit, MoyenPaiement
from .forms import VoyageForm, ConnexionForm, InscriptionForm,MessageForm,MoyenPaiementForm, LitigeForm
from .forms import MessageLitigeForm, RoleForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login,update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .signals import credit_achete 
from django.db.models import Avg
from django.contrib.auth import login, logout
from django.utils import timezone
from django.db.models import Count, Sum, Min
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import AvisForm, VoitureForm, PageForm, PresentationUtilisateurForm, TemoignageForm
from django.http import JsonResponse, HttpResponseForbidden
import requests
from geopy.distance import geodesic
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from django.core.paginator import Paginator
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.db.models.functions import TruncDate


def uml(request):
    return render(request, "apps/home/diagramme-uml.html")

#Espace Administrateur 

#Empêcher la connexion à des personnes qui ne sont pas administrateurs au panel admin
def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)
# Administrateur - Créer un Employé
@superuser_required
def creer_employe(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': "Nom d'utilisateur déjà pris."})
        
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            is_staff=True,
        )
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': "Requête invalide."})

#Dashboard Admin
@superuser_required
def espace_admin(request):
    site = Site.objects.first()
    # Définir la période : aujourd'hui et les 6 jours précédents (7 jours au total)
    today = now().date()
    date_7j = today - timedelta(days=6)

    # Covoiturages par jour
    covoits = (
        Voyage.objects
        .filter(date_depart__date__range=(date_7j, today))
        .annotate(jour=TruncDate('date_depart'))
        .values('jour')
        .annotate(total=Count('id'))
        .order_by('jour')
    )

    # Crédits gagnés par jour (via factures)
    credits = (
        Facture.objects
        .filter(date_facture__range=(date_7j, today))
        .annotate(jour=TruncDate('date_facture'))
        .values('jour')
        .annotate(montant=Sum('montant'))
        .order_by('jour')
    )

    # Total des crédits
    total_credit = Facture.objects.aggregate(total=Sum('montant'))['total'] or 0

    # Préparer les labels (dates formatées) pour les 7 derniers jours
    labels = [(date_7j + timedelta(days=i)).strftime("%d/%m") for i in range(7)]

    # Convertir les résultats en dictionnaires accessibles par date formatée
    covoits_dict = {item['jour'].strftime("%d/%m"): item['total'] for item in covoits}
    credits_dict = {item['jour'].strftime("%d/%m"): item['montant'] or 0 for item in credits}

    # Construire les listes ordonnées des valeurs pour l'affichage (correspondant aux labels)
    covoiturages_totaux = [covoits_dict.get(date, 0) for date in labels]
    credits_montants = [credits_dict.get(date, 0) for date in labels]

    # Récupérer tous les utilisateurs
    users = User.objects.all()

    # Rendu du template
    return render(request, 'apps/admin/espace-admin.html', {
        "site":site,
        'labels': labels,
        'covoiturages_totaux': covoiturages_totaux,
        'credits_montants': credits_montants,
        'total_credit': total_credit,
        'users': users,
    })
#Administrateur - Suspendre un utilisateur     
@superuser_required
def suspendre_utilisateur(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f"{user.username} a été suspendu.")
    return redirect('apps:espace_admin')

#Administrateur - Réactiver un utilisateur
@superuser_required
def reactiver_utilisateur(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"{user.username} a été réactivé.")
    return redirect('apps:espace_admin')

#Passager/conducteur - inscription
def inscription_view(request):
    site = Site.objects.first()
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Création automatique du profil utilisateur
            ProfilUtilisateur.objects.create(utilisateur=user)

            login(request, user)
            messages.success(request, "Inscription réussie.")
            return redirect('apps:home')
    else:
        form = InscriptionForm()
    return render(request, 'apps/user/inscription.html', {'form': form, 'site': site,})

#Tous profils - déconnexion
def deconnexion_view(request):
    
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('apps:connexion')

#Tous profils - connexion 
def connexion_view(request):
    site = Site.objects.first()
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                return redirect('apps:home')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = ConnexionForm()

    return render(request, 'apps/user/connexion.html', {'form': form, 'site':site,})

#Conducteur/Passager - récupérer les informations du profil
def presentation_utilisateur_json(request, pk):
    profil = PresentationUtilisateur.objects.get(pk=pk)
    return JsonResponse({
        "titre": profil.titre,
        "sous_titre": profil.sous_titre,
        "description_courte": profil.description_courte,
        "cover_image": profil.cover_image.url if profil.cover_image else "",
        "raison_1_titre": profil.raison_1_titre,
        "raison_1_description": profil.raison_1_description,
        "raison_1_icone": profil.raison_1_icone or "",
        "raison_2_titre": profil.raison_2_titre,
        "raison_2_description": profil.raison_2_description,
        "raison_2_icone": profil.raison_2_icone or "",
        "raison_3_titre": profil.raison_3_titre,
        "raison_3_description": profil.raison_3_description,
        "raison_3_icone": profil.raison_3_icone or "",
    })

#Site Vitrine - index 
def index(request):
    site = Site.objects.first()
    profils = PresentationUtilisateur.objects.all()

    # Agrégation par trajet pour avoir les trajets les plus fréquents
    voyages_groupes = (
        Voyage.objects
        .filter(date_depart__gte=timezone.now())
        .values('depart', 'arrivee')
        .annotate(
            total=Count('id'),
            prochain_voyage=Min('date_depart')
        )
        .order_by('-total')[:3]
    )

    # Enrichissement avec les détails du prochain voyage
    voyages_details = []
    for v in voyages_groupes:
        trajet = Voyage.objects.filter(
            depart=v['depart'],
            arrivee=v['arrivee'],
            date_depart=v['prochain_voyage']
        ).first()

        if trajet:
            voyages_details.append({
                'depart': v['depart'],
                'arrivee': v['arrivee'],
                'total': v['total'],
                'prix': trajet.prix,
                'date': trajet.date_depart
            })

    return render(request, 'apps/home/index.html', {
        'site': site,
        'profils': profils,
        'voyages_populaires': voyages_details,
    })

# Passager/conducteur - Dashboard
def dashboard_view(request):
    user = request.user
    site = Site.objects.first()
    # Derniers covoiturages réalisés
    voyages_passes = Reservation.objects.filter(
        passager=user,
        voyage__date_depart__lt=timezone.now()
    ).order_by('-voyage__date_depart')[:5]

    # Prochain covoiturage
    voyage_prochain = Reservation.objects.filter(
        passager=user,
        voyage__date_depart__gte=timezone.now()
    ).order_by('voyage__date_depart').first()

    # Messages récents
    messages_recus = Message.objects.filter(destinataire=user).order_by('-date_envoye')[:5]

    context = {
        'site': site,
        "voyages_passes": voyages_passes,
        "voyage_prochain": voyage_prochain,
        "messages_recus": messages_recus,
    }
    return render(request, 'apps/user/dashboard.html', context)

# Gestionnaire - Dashboard
@staff_member_required
def espace_staff(request):
    site = Site.objects.first()
    return render(request, "apps/admin/espace-staff.html", {'site':site} )

#Gestionnaire - accéder aux voyages (single)
@staff_member_required
def detail_voyage_admin(request, voyage_id):
    voyage = get_object_or_404(Voyage, id=voyage_id)
    return render(request, 'apps/admin/covoiturage_detail.html', {'voyage': voyage})

#Gestionnaire - accéder à la liste des voyages 
@staff_member_required
def liste_voyages_admin(request):
    voyages = Voyage.objects.all().order_by('-date_depart')
    return render(request, 'apps/admin/covoiturages-list.html', {'voyages': voyages})

#Gestionnaire - Modifier un voyage 
@staff_member_required
def modifier_voyage_admin(request, voyage_id):
    voyage = get_object_or_404(Voyage, id=voyage_id)
    if request.method == 'POST':
        form = VoyageForm(request.POST, instance=voyage)
        if form.is_valid():
            form.save()
            return redirect('apps:detail_voyage_admin', voyage_id=voyage.id)
    else:
        form = VoyageForm(instance=voyage)

    return render(request, 'apps/admin/modifier_voyage.html', {'form': form, 'voyage': voyage})
#Gestionnaire - Supprimer un voyage 
@staff_member_required
def supprimer_voyage_admin(request, voyage_id):
    voyage = get_object_or_404(Voyage, id=voyage_id)
    if request.method == 'POST':
        voyage.delete()
        return redirect('apps:liste_voyages_admin')
    return render(request, 'apps/admin/confirmer_suppression_voyage.html', {'voyage': voyage})

#Vitrine - Page de contact
def contact(request):
    site = Site.objects.first()
    success = False
    if request.method == "POST":
        nom = request.POST.get("nom")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Exemple : envoi d'email (adapter les paramètres selon ton config)
        send_mail(
            subject=f"Nouveau message de {nom}",
            message=message,
            from_email=email,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )
        success = True

    return render(request, "apps/home/contact.html", {"success": success, 'site':site})

#Tous profils - Messagerie 
@login_required
def messagerie_view(request, litige_id=None):
    user = request.user
    site = Site.objects.first()
    # Récupérer les messages envoyés et reçus pour la messagerie générale
    messages_recus = Message.objects.filter(destinataire=user).order_by('-date_envoye')
    messages_envoyes = Message.objects.filter(expediteur=user).order_by('-date_envoye')

    if litige_id:
        # Si un litige est spécifié, récupérer le litige et ses messages
        litige = get_object_or_404(Litige, id=litige_id)
        messages_litige = litige.messages.order_by('date_envoi')

        if request.method == 'POST':
            form = MessageLitigeForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.litige = litige
                message.auteur = user
                message.save()
                messages.success(request, "Message de litige envoyé.")
                return redirect('apps:messagerie', litige_id=litige.id)
        else:
            form = MessageLitigeForm()

        return render(request, 'apps/litiges/detail.html', {
            'site':site,
            'litige': litige,
            'messages_litige': messages_litige,
            'form': form,
            'messages_recus': messages_recus,
            'messages_envoyes': messages_envoyes,
        })
    else:
        # Si aucun litige n'est sélectionné, afficher uniquement la messagerie générale
        if request.method == 'POST':
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.expediteur = user
                message.save()
                messages.success(request, "Message envoyé.")
                return redirect('apps:messagerie')
        else:
            form = MessageForm()

        return render(request, 'apps/user/messagerie.html', {
            'site':site,
            'form': form,
            'messages_recus': messages_recus,
            'messages_envoyes': messages_envoyes,
        })
        
#Accès à l'API nominatim         
def geocode_city(city_name):
    """Retourne (lat, lon) pour une ville via l'API de Nominatim."""
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': city_name,
        'format': 'json',
        'limit': 1
    }
    response = requests.get(url, params=params, headers={'User-Agent': 'voyage-app'})
    results = response.json()
    if results:
        return float(results[0]['lat']), float(results[0]['lon'])
    return None
        
#Vitrine - Liste des voyages         
def liste_voyages(request):
    site = Site.objects.first()
    voyages_qs = Voyage.objects.annotate(
        moyenne_avis=Avg('avis__note'),
        nb_avis_conducteur=Count('conducteur__voyages__avis')
    ).order_by('-date_depart')

    depart = request.GET.get('depart')
    arrivee = request.GET.get('arrivee')
    date = request.GET.get('date')
    ecologique = request.GET.get('ecologique')
    rayon = request.GET.get('rayon')
    conducteur_avec_avis = request.GET.get('conducteur_avec_avis')  # Nouveau filtre

    # Filtrer voyages écologiques ou non
    if ecologique == 'on':
        voyages_qs = voyages_qs.filter(ecologique=True)
    elif ecologique == 'off':
        voyages_qs = voyages_qs.filter(ecologique=False)

    # Filtrer uniquement voyages dont le conducteur a au moins un avis
    if conducteur_avec_avis == 'on':
        # Garder que les voyages dont le conducteur a au moins un avis sur ses voyages
        voyages_qs = voyages_qs.filter(nb_avis_conducteur__gt=0)

    if date:
        voyages_qs = voyages_qs.filter(date_depart__date=date)

    if depart and rayon:
        rayon_km = float(rayon)
        coords_depart = geocode_city(depart)
        if coords_depart:
            voyages_proches_ids = []
            for voyage in voyages_qs:
                coords_voyage = geocode_city(voyage.depart)
                if coords_voyage:
                    try:
                        distance = geodesic(coords_depart, coords_voyage).km
                        if distance <= rayon_km:
                            voyages_proches_ids.append(voyage.id)
                    except:
                        pass
            voyages_qs = voyages_qs.filter(id__in=voyages_proches_ids)

    if arrivee:
        voyages_qs = voyages_qs.filter(arrivee__icontains=arrivee)

    note_min = request.GET.get('note_min')
    if note_min:
        try:
            note_min = int(note_min)
            if 1 <= note_min <= 5:
                voyages_qs = voyages_qs.filter(moyenne_avis__gte=note_min)
        except ValueError:
            pass
    
    paginator = Paginator(voyages_qs, 6)
    page_number = request.GET.get('page')
    voyages = paginator.get_page(page_number)

    return render(request, 'apps/home/liste-voyage.html', {
        'voyages': voyages,
        'site': site
    })

def voyage_single(request):
    return render(request, "apps/home/voyage-single.html")

#Vitrine - Réserver un voyage (connexion obligatoire)
def reserver_voyage(request, voyage_id):
    site = Site.objects.first()
    voyage = get_object_or_404(Voyage, id=voyage_id)
    if not request.user.is_authenticated:
        messages.warning(request, "Vous devez vous connecter pour voir le détail des covoiturages.")
        return redirect('apps:connexion')
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            if voyage.reserver_place():
                reservation = Reservation(voyage=voyage, passager=request.user, montant=voyage.prix)
                reservation.save()
                return render(request, 'apps/user/confirmation_reservation.html', {'voyage': voyage})
            else:
                return render(request, 'apps/user/erreur_reservation.html', {'message': "Aucune place disponible"})
        else:
            return redirect('apps:connexion')
    return render(request, 'apps/home/reserver-voyage.html', {'voyage': voyage, 'site': site,})

#Passager/conducteur - Voir les voyages réservés
@login_required
def mes_voyages(request):
    utilisateur = request.user
    voyages_conducteur = Voyage.objects.filter(conducteur=utilisateur)
    voyages_passager = Voyage.objects.filter(reservations__passager=utilisateur).distinct()

    return render(request, 'apps/user/covoiturage.html', {
        'voyages_conducteur': voyages_conducteur,
        'voyages_passager': voyages_passager,
    })

#Passager/conducteur - Démarrer un Voyage depuis l'application
@login_required
def demarrer_voyage(request, voyage_id):
    voyage = get_object_or_404(Voyage, id=voyage_id, conducteur=request.user)
    if voyage.etat == 'A_VENIR':
        voyage.etat = 'EN_COURS'
        voyage.save()
        messages.success(request, "Voyage démarré.")
    return redirect('apps:mes_voyages')

#Passager/conducteur - laisser un avis 
def send_mail_avis(passager, voyage):
    send_mail(
        subject="Merci de valider votre covoiturage",
        message=f"Bonjour {passager.username}, veuillez valider votre trajet {voyage.titre}.",
        from_email="noreply@tonsite.com",
        recipient_list=[passager.email],
    )
#Passager/conducteur - Terminer un voyage 
@login_required
def terminer_voyage(request, voyage_id):
    voyage = get_object_or_404(Voyage, id=voyage_id, conducteur=request.user)
    if voyage.etat == 'EN_COURS':
        voyage.etat = 'TERMINE'
        voyage.save()
        # envoyer mail aux passagers
        for reservation in voyage.reservations.all():
            send_mail_avis(reservation.passager, voyage)
        messages.success(request, "Voyage terminé. Les passagers vont être notifiés.")
    return redirect('apps:mes_voyages')

#Conducteur - Créer un voyage
@login_required
def creer_voyage(request):
    profil = request.user.profilutilisateur
    if not profil.est_conducteur:
        messages.error(request, "Vous devez être conducteur pour créer un voyage.")
        return redirect('apps:settings')
    site = Site.objects.first()
    if not request.user.is_authenticated:
        messages.warning(request, "Vous devez vous connecter pour créer un voyage.")
        return redirect('apps:connexion')

    if request.method == 'POST':
        form = VoyageForm(request.POST)
        if form.is_valid():
            voyage = form.save(commit=False)
            voyage.conducteur = request.user 
            voyage.save()
            return redirect('apps:mes_voyages')
    else:
        form = VoyageForm()

    return render(request, 'apps/user/creer-voyage.html', {'form': form, 'site': site})

#Passager/conducteur - Ajouter un moyen de paiement 
@login_required
def ajouter_moyen_paiement(request):
    site = Site.objects.first()
    if request.method == 'POST':
        form = MoyenPaiementForm(request.POST)
        if form.is_valid():
            moyen = form.save(commit=False)
            moyen.utilisateur = request.user
            moyen.save()
            return redirect('apps:ajouter-moyen-paiement') 
    else:
        form = MoyenPaiementForm()
    return render(request, 'apps/user/add_moyens_paiement.html', {'form': form, 'site':site,})

#Passager/conducteur - Acheter des crédits
@login_required
def acheter_credits(request):
    site = Site.objects.first()
    user = request.user
    moyens = MoyenPaiement.objects.filter(utilisateur=user)

    if request.method == 'POST':
        montant = int(request.POST.get('montant', 0))
        moyen_id = request.POST.get('moyen_paiement')

        if montant > 0 and moyen_id:
            moyen = get_object_or_404(MoyenPaiement, id=moyen_id, utilisateur=user)

            # Traitement fictif du paiement ici...

            # Ajouter les crédits
            credit, _ = Credit.objects.get_or_create(utilisateur=user)
            credit.ajouter(montant)

            # Émettre un signal (pour créer une facture automatiquement)
            credit_achete.send(sender=acheter_credits.__class__, utilisateur=user, montant=montant)

            return redirect('apps:ajouter-moyen-paiement')  # ou une page de confirmation

    return render(request, 'apps/user/credits.html', {
        'site':site,
        'moyens_paiement': moyens,
    })

#Gestionnaire - accès au détail des litiges 
@staff_member_required
def litige_detail(request, litige_id):
    litige = get_object_or_404(Litige, id=litige_id)
    return render(request, 'apps/admin/litige_detail.html', {'litige': litige})
#Gestionnaire - liste des litiges 
@staff_member_required
def liste_litiges(request):
    litiges_list = Litige.objects.all().order_by('-date_ouverture')
    paginator = Paginator(litiges_list, 10)  # 10 litiges par page
    page_number = request.GET.get('page')
    litiges = paginator.get_page(page_number)

    return render(request, 'apps/admin/litiges.html', {'litiges': litiges})

#Gestionnaire - clôre un litige
@staff_member_required
def supprimer_litige(request, litige_id):
    litige = get_object_or_404(Litige, id=litige_id)
    litige.delete()
    return redirect('apps:liste_litiges')

#Passager/conducteur - Signaler un litige 
@login_required
def signaler_litige(request):
    site = Site.objects.first()
    if request.method == 'POST':
        form = LitigeForm(request.POST, user=request.user)
        if form.is_valid():
            litige = form.save(commit=False)
            litige.utilisateur = request.user
            litige.save()
            return redirect('apps:voir_litige', litige_id=litige.id)
    else:
        form = LitigeForm(user=request.user)

    return render(request, 'apps/user/litiges.html', {'form': form, "site": site,})

#Passager/conducteur - Laisser un avis 
@login_required
def laisser_avis(request, voyage_id):
    site = Site.objects.first()
    voyage = get_object_or_404(Voyage, id=voyage_id)

    if not Reservation.objects.filter(voyage=voyage, passager=request.user).exists():
        return HttpResponseForbidden("Vous n'avez pas participé à ce voyage.")

    if Avi.objects.filter(voyage=voyage, auteur=request.user).exists():
        return redirect('apps:liste_voyages')  # ou une page avec message

    if request.method == 'POST':
        form = AvisForm(request.POST)
        if form.is_valid():
            avis = form.save(commit=False)
            avis.voyage = voyage
            avis.auteur = request.user
            avis.save()
            return redirect('apps:liste_voyages')
    else:
        form = AvisForm()

    return render(request, 'apps/user/laisser-avis.html', {'form': form, 'voyage': voyage, 'site': site})

#Passager/conducteur - Voir les crédits restants sur le compte 
@login_required
def mes_credits(request):
    site = Site.objects.first()
    factures = Facture.objects.filter(utilisateur=request.user).order_by('-date_facture')
    total_credits = factures.aggregate(total=Sum('montant'))['total'] or 0

    return render(request, 'apps/user/credits.html', {
        'site': site,
        'factures': factures,
        'total_credits': total_credits,
    })
    

#Passager/conducteur - Réserver un Voyage 
@login_required
def reserver_voyage(request, voyage_id):
    site = Site.objects.first()
    voyage = get_object_or_404(Voyage, id=voyage_id)

    # Vérifier qu'il reste de la place
    if voyage.nb_places_restantes <= 0:
        return render(request, 'apps/user/erreur-reservation.html', {
            'message': "Aucune place disponible.",
            'site': site
        })

    # Vérifier que l'utilisateur a assez de crédits
    credit, _ = Credit.objects.get_or_create(utilisateur=request.user)
    if credit.montant < 2:
        return render(request, 'apps/user/erreur-reservation.html', {
            'message': "Vous n'avez pas assez de crédits pour réserver ce voyage.",
            'site': site
        })

    # Confirmation
    if request.method == 'POST' and 'confirm' in request.POST:
        # Réserver la place
        if voyage.reserver_place():
            reservation = Reservation.objects.create(
                voyage=voyage,
                passager=request.user,
                montant=voyage.prix
            )
            # Décrémenter les crédits
            credit.retirer(2)
            return render(request, 'apps/user/confirmation.html', {
                'voyage': voyage,
                'reservation': reservation,
                'site': site
            })
        else:
            return render(request, 'apps/user/erreur-reservation.html', {
                'message': "La réservation a échoué, aucune place disponible.",
                'site': site
            })
    # Première visite => demande de confirmation
    return render(request, 'apps/user/confirmation-reservation.html', {
        'voyage': voyage,
        'credit_disponible': credit.montant,
        'site': site
    })

#Passager/conducteur - Settings            
@login_required
def settings_view(request):
    profil = request.user.profilutilisateur
    if request.method == 'POST':
        role_form = RoleForm(request.POST, instance=profil)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)

        if 'update_roles' in request.POST and role_form.is_valid():
            role_form.save()
            return redirect('apps:settings')

        elif 'update_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Pour rester connecté après changement
            return redirect('apps:settings')
    else:
        role_form = RoleForm(instance=profil)
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'apps/user/settings.html', {
        'role_form': role_form,
        'password_form': password_form,
    })

    
#Gestionnaire - liste des avis
@staff_member_required
def avis_liste(request):
    site = Site.objects.first()
    liste_avis = Avi.objects.all().order_by('-date')
    paginator = Paginator(liste_avis, 10)  # 10 avis par page

    page = request.GET.get('page')
    avis = paginator.get_page(page)

    return render(request, 'apps/admin/avis-list.html', {
        'avis': avis,
        'site': site,
    })

#Gestionnaire - valider un avis après relecture
@staff_member_required
def valider_avis(request, avis_id):
    avis = get_object_or_404(Avi, id=avis_id)
    avis.est_affiche = True
    avis.save()
    return redirect('apps:avis_liste')

#Gestionnaire - Supprimer un avis après relecture 
@staff_member_required
def supprimer_avis(request, avis_id):
    avis = get_object_or_404(Avi, id=avis_id)
    avis.delete()
    return redirect('apps:avis_liste')

#API - Marque des véhicules 
def get_modeles(request):
    marque = request.GET.get('marque')
    if not marque:
        return JsonResponse({'error': 'Marque requise'}, status=400)

    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/GetModelsForMake/{marque}?format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        modeles = sorted(set(item['Model_Name'] for item in data['Results']))
        return JsonResponse({'modeles': modeles})
    return JsonResponse({'error': 'Échec de l’appel API'}, status=500)

#Conducteur - Ajouter un véhicule
def ajouter_voiture(request):
    site = Site.objects.first()
    marques = ["Toyota", "Renault", "BMW", "Peugeot", "Mercedes", "Audi", "Volkswagen"]  # Exemples de marques

    if request.method == 'POST':
        form = VoitureForm(request.POST, request.FILES)
        if form.is_valid():
            voiture = form.save(commit=False)
            voiture.proprietaire = request.user
            voiture.save()
            return redirect('apps:dashboard')
    else:
        form = VoitureForm()

    return render(request, 'apps/user/ajouter_voiture.html', {
        'form': form,
        'site': site,
        'marques': marques
    })

#Vitrine - Ajouter des pages (blog ou témoignage)
def page_detail(request, page_id):
    site = Site.objects.first()
    page = Page.objects.get(id=page_id)
    
    return render(request, 'apps/home/page_detail.html', {
        'page': page,
        'site':site,
    })
    
#Vitrine - Gestion des pages (blog ou témoignage)    
def gestion_pages(request, page_id=None):
    site = Site.objects.first()
    page_instance = get_object_or_404(Page, id=page_id) if page_id else None
    type_page = request.POST.get('type_page') if request.method == 'POST' else page_instance.type_page if page_instance else None

    page_form = PageForm(request.POST or None, request.FILES or None, instance=page_instance)

    # Initialiser les bons sous-formulaires
    presentation_form = PresentationUtilisateurForm(request.POST or None, request.FILES or None)
    temoignage_form = TemoignageForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if 'delete' in request.POST:
            Page.objects.filter(id=request.POST.get('delete')).delete()
            return redirect('apps:gestion_pages')

        if page_form.is_valid():
            # Sauver la page
            page = page_form.save()

            if type_page == 'utilisateurs' and presentation_form.is_valid():
                presentation = presentation_form.save()
                page.presentation = presentation
                page.save()
            elif type_page == 'temoignages' and temoignage_form.is_valid():
                temoignage = temoignage_form.save()
                page.temoignage = temoignage
                page.save()


            return redirect('apps:gestion_pages')

    pages = Page.objects.all()
    return render(request, 'apps/admin/gestion_pages.html', {
        'site':site,
        'page_form': page_form,
        'presentation_form': presentation_form,
        'temoignage_form': temoignage_form,
        'pages': pages,
        'selected_type': type_page,
        'page_instance': page_instance
    })
    
#Conducteur/passager - Présentation de l'utilisateur     
def presentation_utilisateur_detail(request, page_id):
    site = Site.objects.first()
    page = PresentationUtilisateur.objects.get(id=page_id)
    
    return render(request, 'apps/admin/user_detail.html', {
        'site':site,
        'page': page,
    })
#Vitrine - Page détail (Témoignage)
def temoignage_detail(request, page_id):
    site = Site.objects.first()
    temoignage = Temoignage.objects.get(id=page_id)
    
    return render(request, 'apps/admin/temoignage_detail.html', {
        'site':site,
        'temoignage': temoignage,
    })
#Conducteur/passager - Gestion de la présentation des utilisateurs
def gestion_presentation_utilisateur(request, instance_id=None):
    site = Site.objects.first()
    instance = get_object_or_404(PresentationUtilisateur, id=instance_id) if instance_id else None

    if request.method == 'POST':
        if 'delete' in request.POST:
            instance_to_delete = get_object_or_404(PresentationUtilisateur, id=request.POST.get('delete'))
            instance_to_delete.delete()
            return redirect('apps:gestion_presentation_utilisateur')

        form = PresentationUtilisateurForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('apps:gestion_presentation_utilisateur')
    else:
        form = PresentationUtilisateurForm(instance=instance)

    toutes_presentations = PresentationUtilisateur.objects.all()

    return render(request, 'apps/admin/gestion_presentation.html', {
        'site':site,
        'form': form,
        'presentations': toutes_presentations,
        'instance': instance,
    })    


# === VUE COMBINÉE POUR TEMOIGNAGE ===
#Vitrine -
def gestion_temoignage(request, instance_id=None):
    site = Site.objects.first()
    instance = get_object_or_404(Temoignage, id=instance_id) if instance_id else None

    if request.method == 'POST':
        if 'delete' in request.POST:
            instance_to_delete = get_object_or_404(Temoignage, id=request.POST.get('delete'))
            instance_to_delete.delete()
            return redirect('gestion_temoignage')

        form = TemoignageForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect('gestion_temoignage')
    else:
        form = TemoignageForm(instance=instance)

    tous_temoignages = Temoignage.objects.all()

    return render(request, 'apps/admin/gestion_temoignage.html', {
        'site':site,
        'form': form,
        'temoignages': tous_temoignages,
        'instance': instance,
    })
    
# Vue pour afficher toutes les factures
def liste_factures(request):
    site = Site.objects.first()
    factures_list = Facture.objects.all().order_by('-date_facture')
    paginator = Paginator(factures_list, 10)  

    page_number = request.GET.get('page')
    factures = paginator.get_page(page_number)

    return render(request, 'apps/admin/factures.html', {'factures': factures, 
                                                        'site':site,})

# Vue pour afficher une facture spécifique
def detail_facture(request, facture_id):
    site = Site.objects.first()
    facture = get_object_or_404(Facture, pk=facture_id)
    return render(request, 'apps/admin/facture-single.html', {'facture': facture, 
                                                              'site':site,})
    
@staff_member_required
def marquer_paye(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    facture.est_paye = True
    facture.save()
    return redirect('apps:liste_factures')

@staff_member_required
def supprimer_facture(request, facture_id):
    facture = get_object_or_404(Facture, id=facture_id)
    facture.delete()
    return redirect('apps:liste_factures')