# Utiliser une image Python légère
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Mettre à jour les paquets et installer les dépendances nécessaires pour ODBC
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    odbcinst \
    lsb-release \
    ca-certificates \
    apt-transport-https \
    && curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/$(lsb_release -rs)/prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements.txt et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code source dans le conteneur
COPY . .

# Copier le fichier .env dans le conteneur
COPY .env /app/.env

# Installer Gunicorn
RUN pip install gunicorn

RUN python manage.py collectstatic --noinput

# Exposer le port 8001 (pour Django)
EXPOSE 8001

# Commande pour lancer l'application Django avec Gunicorn
#CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--log-level", "debug", "filmprediction.wsgi:application"]
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--workers", "9", "--log-level", "debug", "filmprediction.wsgi:application"]
