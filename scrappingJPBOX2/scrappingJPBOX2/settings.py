# Scrapy settings for scrappingJPBOX project
BOT_NAME = "scrappingJPBOX2"

SPIDER_MODULES = ["scrappingJPBOX2.spiders"]
NEWSPIDER_MODULE = "scrappingJPBOX2.spiders"

# Crawl responsibly by identifying yourself
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Les paramètres de concurrence définis dans le spider via custom_settings auront priorité sur ces valeurs
CONCURRENT_REQUESTS = 4
DOWNLOAD_DELAY = 2

# Configure item pipelines
ITEM_PIPELINES = {
   'scrappingJPBOX2.pipelines.ScrappingjpboxPipeline': 300,
}

# Enable and configure the AutoThrottle extension
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Configuration de l'exportation des données
FEED_FORMAT = 'csv'
FEED_URI = 'exports/jpbox_films_%(time)s.csv'  # Utilise un timestamp pour éviter les écrasements
FEED_EXPORT_ENCODING = 'utf-8-sig'  # Pour la compatibilité avec Excel (caractères accentués)
FEED_EXPORTERS = {
    'csv': 'scrapy.exporters.CsvItemExporter',
}

# Configuration CSV spécifique pour le français
FEED_EXPORT_FIELDS = [
    'film_id', 'titre', 'genre_principale', 'genres', 'date_sortie_france', 
    'date_sortie_usa', 'duree_minutes', 'synopsis', 'realisateur', 'acteurs', 
    'pays_origine', 'budget','box_office_demarrage', 'box_office_france', 'recette_usa', 
    'recette_monde', 'image_url', 'note_moyenne'
]

# Paramètres du CSV
FEED_EXPORT_DELIMITER = ';'  # Utiliser point-virgule comme délimiteur (standard français)

# Activer les logs
LOG_ENABLED = True
LOG_LEVEL = 'DEBUG'
LOG_FILE = 'jpbox_scraping.log'  # Sauvegarder les logs dans un fichier

# Paramètres pour éviter d'être bloqué
COOKIES_ENABLED = False
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429, 403]