# Scrapy settings for monprojet project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# Scrapy settings for jpbox_office_scraper project
# Scrapy settings for scrapping project
BOT_NAME = "scrapping"

SPIDER_MODULES = ["scrapping.spiders"]
NEWSPIDER_MODULE = "scrapping.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy
CONCURRENT_REQUESTS = 4

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 2  # 2 seconds of delay to avoid being blocked

# Configure item pipelines
ITEM_PIPELINES = {
   "scrapping.pipelines.JpboxOfficeScraperPipeline": 300,
}

# Enable and configure the AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Configuration de l'exportation des données
FEED_FORMAT = 'csv'
#FEED_URI = 'jpbox_films.csv'
FEED_EXPORT_ENCODING = 'utf-8'

# Activer les logs
LOG_ENABLED = True
LOG_LEVEL = 'INFO'

# Configuration des champs pour l'exportation CSV
# Configuration des champs pour l'exportation CSV
FEED_EXPORT_FIELDS = [
    'film_id',
    'titre',
    'genre_principale',
    'date_sortie_france',
    'date_sortie_usa',
    'image_url',
    'synopsis',
    'duree',                   
    'note_moyenne',
    'acteurs',          
    'entrees_demarrage_france',
    'entrees_totales_france',
    'budget',
    'recette_usa',
    'recette_monde',
    'total_salles'
]

custom_settings = {
    'DOWNLOAD_DELAY': 3,  # 3 secondes entre chaque requête
    'CONCURRENT_REQUESTS_PER_DOMAIN': 2,  # Maximum 2 requêtes simultanées
    # Autres paramètres...
}