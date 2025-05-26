# ecorideecf

Bonjour ! 
Merci de venir voir mon projet ecoride. 
 
Ici vous retrouverez le lien pour accéder à l'application : [ecorideecf](https://ecorideecf-production.up.railway.app/)

Cette application a été lancée sur un serveur Railway. 
Il s'agit d'une application dévéloppée en Django, PostgreSQL, HTML et CSS. J'utilise également Boostrap. 

Le lien pour accéder au schéma UML ainsi qu'à la base de données se trouve sur le site internet. 

Ce lien mène vers un lien de téléchargement wetransfer (valable 3j) pour télécharger les différents parcours utilisateurs, avec leurs différentes explications. 
Lien : https://we.tl/t-k0FntQVfS5

Le lien vers le design figma se trouve ici : 
https://www.figma.com/proto/dbGSqUXDVmRwE9pgNplnY2/ecoride-ecf?node-id=0-1&t=oyws34J6XlnTPju9-1

En revanche, je ne suis pas designeuse. Je sais utiliser l'API de figma et faire des call dessus, mais pas me servir correctement de figma.

J'ai utilisé un outil pour retranscrire le code HTML de mon site internet (si je devais travailler avec un.e UX/UI designer). 

Pour déployer l'application sur vos serveurs, suivez les manipulations suivantes : 

Pré-requis : 

Python (3.8+)

pip 

Git

virtualenv ou venv

git clone https://github.com/beeofpossible/ecorideecf.git

cd ecorideecf

Sous Windows : 

python -m venv env

env\Scripts\activate


Sous Mac: 

python3 -m venv env

source env/bin/activate 

Installer les dépendances : 

pip install -r requirements.txt

Appliquer les migrations : 

py main.py makemigrations 

py main.py migrate 

Créer un superutilisateur :

py main.py createsuperuser

Lancer le serveur :

py main.py runserver

