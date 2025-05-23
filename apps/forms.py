from django import forms
from .models import ProfilUtilisateur, Site, Voyage, Reservation, Message, MoyenPaiement, Litige, Avi, Voiture
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Page, PresentationUtilisateur, Temoignage, Facture
from django.contrib.auth.forms import PasswordChangeForm


class ConnexionForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': "Nom d'utilisateur"
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': "Mot de passe"
        })
    )
    
class InscriptionForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return self.cleaned_data['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class ProfilUtilisateurForm(forms.ModelForm):
    class Meta:
        model = ProfilUtilisateur
        fields = ['utilisateur', 'est_conducteur', 'bio']
        
    def __init__(self, *args, **kwargs):
        super(ProfilUtilisateurForm, self).__init__(*args, **kwargs)
        # Optionnel : Personnaliser les widgets pour améliorer l'UI
        self.fields['bio'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 40})

class RoleForm(forms.ModelForm):
    class Meta:
        model = ProfilUtilisateur
        fields = ['est_conducteur', 'est_utilisateur']
        widgets = {
            'est_conducteur': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'est_utilisateur': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'est_conducteur': "Je suis conducteur",
            'est_utilisateur': "Je suis utilisateur",
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['destinataire', 'contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Votre message...'}),
        }
        
class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ['titre', 'description', 'avantage_1', 'avantage_2', 'avantage_3', 'icone_avantage_1', 'icone_avantage_2', 'icone_avantage_3']
        
    def __init__(self, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        # Personnaliser les widgets pour améliorer l'UI
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 40})
        self.fields['avantage_1'].widget = forms.TextInput(attrs={'placeholder': 'Ex: Chargement rapide'})
        self.fields['avantage_2'].widget = forms.TextInput(attrs={'placeholder': 'Ex: Design responsive'})
        self.fields['avantage_3'].widget = forms.TextInput(attrs={'placeholder': 'Ex: Sécurisé'})
        self.fields['icone_avantage_1'].widget = forms.TextInput(attrs={'placeholder': 'Ex: fa-solid fa-check-circle'})
        self.fields['icone_avantage_2'].widget = forms.TextInput(attrs={'placeholder': 'Ex: fa-solid fa-mobile'})
        self.fields['icone_avantage_3'].widget = forms.TextInput(attrs={'placeholder': 'Ex: fa-solid fa-lock'})
        
class VoyageForm(forms.ModelForm):
    date_depart = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Voyage
        fields = ['titre', 'description', 'depart', 'arrivee', 'date_depart', 'places_disponibles', 'prix']
        exclude = ['conducteur']

        widgets = {
            'depart': forms.TextInput(attrs={'list': 'depart_list', 'autocomplete': 'off'}),
            'arrivee': forms.TextInput(attrs={'list': 'arrivee_list', 'autocomplete': 'off'}),
            # le widget date_depart est défini séparément
        }

    def __init__(self, *args, **kwargs):
        super(VoyageForm, self).__init__(*args, **kwargs)
        # Personnaliser les widgets pour améliorer l'UI
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 40})
        self.fields['prix'].widget = forms.NumberInput(attrs={'step': '0.01'})
        
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['voyage', 'passager', 'montant']
        
    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        # Personnaliser les widgets pour améliorer l'UI
        self.fields['montant'].widget = forms.NumberInput(attrs={'step': '0.01'})
        
class VoitureForm(forms.ModelForm):
    class Meta:
        model = Voiture
        fields = ['marque', 'modele', 'couleur', 'immatriculation', 'nombre_places', 'photo']

class MoyenPaiementForm(forms.ModelForm):
    class Meta:
        model = MoyenPaiement
        fields = ['type', 'nom', 'details', 'actif']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'details': forms.TextInput(attrs={'class': 'form-control'}),
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class LitigeForm(forms.ModelForm):
    class Meta:
        model = Litige
        fields = ['type_litige', 'voyage', 'reservation', 'sujet', 'description_initiale']
        widgets = {
            'sujet': forms.TextInput(attrs={'class': 'form-control'}),
            'description_initiale': forms.Textarea(attrs={'class': 'form-control'}),
            'type_litige': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Supprime 'user' pour éviter l'erreur
        super().__init__(*args, **kwargs)

        # Initialiser les queryset par défaut
        self.fields['voyage'].queryset = Voyage.objects.none()
        self.fields['reservation'].queryset = Reservation.objects.none()

        # Si utilisateur fourni, on adapte les querysets selon le type de litige choisi
        if user:
            type_litige = self.initial.get('type_litige') or getattr(self.instance, 'type_litige', None)
            
            if type_litige == 'voyage':
                self.fields['voyage'].queryset = Voyage.objects.filter(conducteur=user)
            elif type_litige == 'reservation':
                self.fields['reservation'].queryset = Reservation.objects.filter(passager=user)


class AvisForm(forms.ModelForm):
    class Meta:
        model = Avi
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.Select(choices=[(i, f"{i} étoile{'s' if i > 1 else ''}") for i in range(1, 6)], attrs={'class': 'form-select'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'placeholder': "Votre retour..."}),
        }

class MessageLitigeForm(forms.ModelForm):
    class Meta:
        model = Litige
        fields = ['type_litige', 'voyage', 'reservation', 'sujet', 'description_initiale']
        widgets = {
            'description_initiale': forms.Textarea(attrs={'rows': 4}),
        }
        
class PresentationUtilisateurForm(forms.ModelForm):
    class Meta:
        model = PresentationUtilisateur
        fields = [
            'titre', 'sous_titre', 'description_courte', 'cover_image', 'miniature_image',
            'raison_1_titre', 'raison_1_description', 'raison_1_icone', 'raison_1_image',
            'raison_2_titre', 'raison_2_description', 'raison_2_icone', 'raison_2_image',
            'raison_3_titre', 'raison_3_description', 'raison_3_icone', 'raison_3_image',
        ]

class TemoignageForm(forms.ModelForm):
    class Meta:
        model = Temoignage
        fields = [
            'titre', 'sous_titre', 'cover_image',
            'temoignage_1_titre', 'temoignage_1_sous_titre', 'temoignage_1_texte', 'temoignage_1_image',
            'temoignage_2_titre', 'temoignage_2_sous_titre', 'temoignage_2_texte', 'temoignage_2_image',
            'temoignage_3_titre', 'temoignage_3_sous_titre', 'temoignage_3_texte', 'temoignage_3_image',
        ]

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = [
            'titre', 'sous_titre', 'description_courte', 'cover_image', 'type_page',
            'section_1_titre', 'section_1_sous_titre', 'section_1_texte', 'section_1_image',
            'section_2_titre', 'section_2_sous_titre', 'section_2_texte', 'section_2_image',
            'section_3_titre', 'section_3_sous_titre', 'section_3_texte', 'section_3_image',
        ]