# New Is Always Better - Cinéma Prediction Tool
## Présentation du projet
"New Is Always Better" est un outil décisionnel développé pour un gérant de cinéma qui souhaite optimiser la sélection des films à projeter. Ce cinéma adopte une politique unique : ne diffuser que les nouveautés lors de leur première semaine, avec un renouvellement hebdomadaire chaque mercredi.
Le cinéma dispose de deux salles (capacités de 120 et 80 spectateurs), et l'objectif de l'outil est de prédire le nombre d'entrées potentielles des films à venir pour maximiser les revenus.

## Architecture globale

Le projet est organisé en microservices :

API de prédiction (FastAPI) : Expose le modèle de machine learning
Application web (Django) : Interface utilisateur pour le gérant
Base de données transactionnelle : Stockage des données de l'application (SQLite)
Base de données analytique : Stockage des données pour le modèle ML (Azure Blob Storage)

## Partie 1 : API de Prédiction (FastAPI)
Cette API permet de faire des prédictions d'entrées pour les films à venir en première semaine d'exploitation.

### Fonctionnalités

Prédiction individuelle : Prédit le nombre d'entrées pour un seul film
Prédiction par lots : Analyse plusieurs films simultanément
Feature Engineering : Transforme les données brutes du film en caractéristiques exploitables
Modèle ML : Utilise CatBoost pour générer des prédictions précises

### Installation
Prérequis

Python 3.8+
pip (gestionnaire de paquets Python)

### Étapes d'installation
bash
# Cloner le dépôt
git clone https://github.com/votre-repo/new-is-always-better.git
cd new-is-always-better/api

## Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

## Installer les dépendances
pip install -r requirements.txt

## Utilisation de l'API
Démarrer l'API
bash# Dans le dossier api/
uvicorn main:app --reload --host 0.0.0.0 --port 8000
L'API sera accessible à l'adresse : http://localhost:8000
Documentation des endpoints
Une fois l'API démarrée, accédez à la documentation interactive à l'adresse :

Swagger UI : http://localhost:8000/docs
ReDoc : http://localhost:8000/redoc

Endpoints principaux
1. Prédiction pour un film
POST /predict
Exemple de requête :
json{
  "film_title": "Avatar 3",
  "release_date": "2025-12-25",
  "duration": "2h 45min",
  "age_classification": "Tout public",
  "producers": "James Cameron,Jon Landau",
  "director": "James Cameron",
  "top_stars": "Sam Worthington,Zoe Saldana",
  "languages": "Anglais",
  "distributor": "20th Century Studios",
  "year_of_production": "2025",
  "film_nationality": "États-Unis",
  "filming_secrets": "15 anecdotes",
  "awards": "",
  "associated_genres": "Science-Fiction,Aventure",
  "broadcast_category": "en salle",
  "trailer_views": "5000000 vues",
  "synopsis": "Jake Sully et Neytiri sont de retour pour une nouvelle aventure épique sur Pandora."
}
Exemple de réponse :
json{
  "film_title": "Avatar 3",
  "predicted_fr_entries": 1250000
}
2. Prédiction pour plusieurs films
POST /predict-batch
Corps de la requête : Liste de films au format JSON
Modèle de prédiction
Algorithme
Le modèle utilise CatBoostRegressor, un algorithme de boosting de gradient optimisé pour les caractéristiques catégorielles.
Caractéristiques utilisées
Les principales caractéristiques utilisées pour la prédiction sont :

Métadonnées du film

Durée
Synopsis (longueur, sentiment)
Prix et nominations
Vues de la bande-annonce
Date de sortie et saison


Équipe de production

Réalisateur
Acteurs principaux
Producteurs


Distribution et franchise

Distributeur (pouvoir dans l'industrie)
Appartenance à une franchise
Licence cinématographique
Univers cinématographique connecté


Caractéristiques binaires

Présence de stars spécifiques
Nationalités du film
Langues utilisées
Studio majeur ou indépendant



Déploiement avec Docker
bash# Construire l'image Docker
docker build -t film-prediction-api .

# Lancer le conteneur
docker run -d -p 8000:8000 film-prediction-api
Fichier Dockerfile
dockerfileFROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
Partie 2 : Application Web (Django)
L'application web fournit une interface utilisateur pour le gérant du cinéma, permettant de visualiser les prédictions, gérer la programmation des salles, et suivre les performances financières.
Fonctionnalités

Dashboard : Vue d'ensemble des films sélectionnés et à venir
Top Ten : Liste des films avec les plus hautes prédictions d'entrées
Recettes : Suivi des entrées réelles et des revenus par salle et par jour
Finances : Analyse du chiffre d'affaires, des coûts et de la rentabilité
Paramètres : Import et mise à jour des données de films

Installation
Prérequis

Python 3.8+
pip (gestionnaire de paquets Python)

Étapes d'installation
bash# Se placer dans le répertoire de l'application Django
cd new-is-always-better/django_app

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur (optionnel)
python manage.py createsuperuser

# Démarrer le serveur de développement
python manage.py runserver
L'application sera accessible à l'adresse : http://localhost:8000

Modèles de données
Movie
Stocke les informations sur chaque film.
Champs principaux :

title : Titre du film
image_url : URL de l'affiche
synopsis : Résumé du film
genre : Genres du film
cast : Acteurs principaux
release_date_fr : Date de sortie en France
first_week_actual_entries_france : Entrées réelles en première semaine

PredictionHistory
Enregistre l'historique des prédictions pour chaque film.
Champs principaux :

movie : Relation au film
first_week_predicted_entries_france : Prédiction d'entrées
prediction_error : Erreur de prédiction calculée
model_version : Version du modèle utilisé
date : Date de la prédiction

Broadcast
Représente une semaine de programmation.
Champs principaux :

start_date : Date de début (mercredi)
end_date : Date de fin (mardi suivant)
room_1 et room_2 : Films projetés dans chaque salle

Recette
Enregistre les entrées et revenus quotidiens.
Champs principaux :

date : Date du jour
ticket_price : Prix du billet
broadcast_id : Semaine de diffusion
room_1_movie et room_2_movie : Films projetés
room_1_actual et room_2_actual : Entrées réelles
consumptions : Revenus additionnels (confiserie, etc.)

Vues principales
Dashboard
Affiche les films actuellement projetés et ceux à venir, avec leurs prédictions d'entrées.
Top Ten
Liste les 10 films avec les prédictions d'entrées les plus élevées pour la semaine à venir.
Recettes
Interface de suivi et mise à jour des entrées réelles pour chaque film, chaque jour et chaque salle.
Finances
Analyse financière avec les métriques clés :

Chiffre d'affaires hebdomadaire
Coûts fixes
Bénéfice net
Taux d'occupation des salles
Comparaison avec les périodes précédentes

Paramètres
Permet d'importer des données de films depuis:

Un fichier CSV uploadé manuellement
Un stockage Azure Blob automatiquement

Fonctionnalités d'Import de Données
L'application permet deux méthodes d'import de données :

Import manuel via CSV

Upload d'un fichier CSV contenant les données des films
Traitement et intégration dans la base de données


Import automatique depuis Azure Blob Storage

Connexion à un conteneur Azure configuré dans les paramètres
Récupération et traitement des données
Génération automatique de prédictions pour les nouveaux films



Logique métier
Sélection des films

Les films sont classés par nombre d'entrées potentielles
Le film avec la plus haute prédiction est attribué à la salle 1 (120 places)
Le deuxième film est attribué à la salle 2 (80 places)

Calcul financier

Recette hebdomadaire = Nombre d'entrées × Prix du billet (10€) + Consommations
Bénéfice = Recette hebdomadaire - Coûts fixes (4900€)
Taux d'occupation = Entrées totales ÷ (Capacité totale des salles × 7 jours)

Déploiement
Avec Docker
bash# Construire l'image Docker
docker build -t new-is-always-better-django .

# Lancer le conteneur
docker run -d -p 8000:8000 new-is-always-better-django
Fichier Dockerfile
dockerfileFROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Appliquer les migrations
RUN python manage.py migrate

# Exposer le port
EXPOSE 8000

# Démarrer le serveur
CMD ["gunicorn", "filmprediction.wsgi:application", "--bind", "0.0.0.0:8000"]
Docker Compose pour l'ensemble du projet
Pour déployer l'ensemble de l'application (API et Interface Web):
yamlversion: '3'

services:
  api:
    build: ./api
    ports:
      - "8001:8000"
    volumes:
      - ./api:/app
    environment:
      - MODEL_PATH=/app/model/catboost_model.cbm
    restart: always

  web:
    build: ./django_app
    ports:
      - "8000:8000"
    volumes:
      - ./django_app:/app
    environment:
      - FASTAPI_URL=http://api:8000
      - SECRET_KEY=your_secret_key
      - DEBUG=0
      - ACCOUNT_URL=your_azure_account
      - CONTAINER_NAME=your_container
      - BLOB_NAME=your_blob
    depends_on:
      - api
    restart: always
Utilisation de l'application

Accéder à l'application via http://localhost:8000
Consulter le tableau de bord pour voir les films actuellement projetés
Explorer l'onglet "Top Ten" pour voir les prédictions des prochaines sorties
Mettre à jour les entrées réelles dans l'onglet "Recettes"
Analyser les performances financières dans l'onglet "Finances"
Importer de nouvelles données via l'onglet "Paramètres"

# Accéder à l application déployée
http://djangoazure.francecentral.azurecontainer.io:8001/

## Maintenance et mises à jour
Mise à jour du modèle

## Mise à jour des données
Effectuer une mise à jour manuelle via l'interface utilisateur :

## Accéder à l'onglet "Paramètres"
Utiliser la fonction "Update Data from blob storage" ou "Upload CSV File"

## Support et contact
Pour toute question ou assistance, veuillez contacter l'équipe de développement.

## À propos du projet
Ce projet a été développé dans le cadre d'une mission pour une ESN, suivant la méthodologie agile SCRUM avec quatre développeurs IA. Il vise à aider le gérant d'un cinéma à optimiser la sélection des films pour maximiser les revenus.
