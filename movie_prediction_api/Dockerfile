# Utilise une image Python comme base
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installation des outils de compilation nécessaires
RUN apt-get update && apt-get install -y build-essential git

# Copier les fichiers de dépendances
COPY requirements.txt .

# Modifier le fichier requirements.txt pour utiliser la dernière version de catboost
RUN sed -i 's/catboost==2.8.0/catboost/g' requirements.txt

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# S'assurer que les droits d'accès sont corrects
RUN chmod -R 755 /app

# Copier le reste du code
COPY ./app /app/app
COPY ./model /app/model

# Exposer le port
EXPOSE 8000

# Commande pour démarrer l'API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]