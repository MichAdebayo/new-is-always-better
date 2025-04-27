# Utilise une image Python comme base
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY requirements.txt .
COPY . .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port de ton API si tu en as une (ex: Flask en 5000)
EXPOSE 5000

# Commande pour démarrer ton application (ajuste selon ton script)
CMD ["python", "main.py"]
