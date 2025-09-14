# 🌱 EcoRide - Projet ECF

Bienvenue, et merci de jeter un œil à mon projet **EcoRide** !

---

## 🔗 Lien vers l'application
L’application est hébergée sur **Railway** :  
👉 [Accéder à EcoRide](https://ecorideecf.railway.app) 

---

## 🛠️ Stack Technique

- **Backend** : Django (Python)
- **Base de données relationnelle** : PostgreSQL (hébergée sur Railway)
- **Base de données NoSQL** : Firebase
- **Frontend** : HTML, CSS, Bootstrap
- **Hébergement** : Railway (pas de Docker ici, ce n’était pas nécessaire)
- **Design** : Figma (généré à partir du code HTML)

---

## 🎨 Design & UX

- 📄 **Parcours utilisateurs (PDF)** : [Lien WeTransfer (valide 3 jours)](https://we.tl/t-k0FntQVfS5)
- 🖌️ **Maquette Figma** : [Voir sur Figma](https://www.figma.com/proto/dbGSqUXDVmRwE9pgNplnY2/ecoride-ecf?node-id=0-1&t=oyws34J6XlnTPju9-1)

> ⚠️ Je ne suis pas designeuse, mais j’ai utilisé mes expériences précédentes et des outils comme l’API Figma pour créer l’interface.

### Inspirations design :
- [Foncia](https://www.foncia.com)
- [BlaBlaCar](https://www.blablacar.fr)

### Charte graphique :
Créée à partir des couleurs du logo/images avec cet outil génial :  
🎨 [imagecolorpicker.com](https://imagecolorpicker.com/fr)

### Images :
- Générées via : [pixlr.com/image-generator](https://pixlr.com/image-generator/)
- Ou libres de droit

---

## 🗃️ Schéma UML & base de données

Le schéma UML et la structure de la base de données sont disponibles directement sur le site de l’application.

---

## 🧪 Déploiement en local

### ✅ Pré-requis :
- Python 3.8+
- `pip`
- `git`
- `virtualenv` ou `venv`

---

### 👇 Étapes d’installation

```bash
# Cloner le projet
git clone https://github.com/beeofpossible/ecorideecf.git
cd ecorideecf

#Sous Windows :

python -m venv env
env\Scripts\activate

#Sous macOS/Linux :

python3 -m venv env
source env/bin/activate

#🔧 Installer les dépendances :

pip install -r requirements.txt

#📦 Appliquer les migrations :

python main.py makemigrations
python main.py migrate

#👤 Créer un superutilisateur :

python main.py createsuperuser

#🚀 Lancer le serveur local :

python main.py runserver
'''
🙌 Merci !
N’hésitez pas à explorer le code, tester, forker ou poser vos questions.
Et surtout… merci encore d’être passé·e voir EcoRide !
