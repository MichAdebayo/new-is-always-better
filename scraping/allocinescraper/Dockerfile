FROM python:3.10-slim

WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpq-dev \
    build-essential \
    gettext \
    && apt-get clean

# Copy only requirements first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
# Copy the Scrapy project code
COPY . .

COPY .env /app/.env

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]

# Commande par défaut pour lancer le spider et uploader le CSV
#CMD ["scrapy", "crawl", "allocine", "-o", "allocine.csv"]
#CMD ["sh", "-c", "scrapy crawl allocine_new_movies"] 
#&& python upload_blob.py"]"""

#CMD ["sh", "-c", "scrapy crawl allocine_new_movies && python upload_blob.py"] 