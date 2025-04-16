# jpbox_config.py
"""
Configuration pour le spider JPBox.
Ce fichier permet de définir facilement les paramètres de scraping sans modifier le code du spider.
"""

# Configuration des périodes à scraper
# Format: liste de dictionnaires avec les années de début et de fin, ainsi qu'une étiquette
PERIODS = [
    {"year": "2000", "year2": "2009", "label": "2000-2009"},
    {"year": "2010", "year2": "2019", "label": "2010-2019"},
    {"year": "2020", "year2": "2029", "label": "2020-2029"},
]

# Nombre maximum de genres à scraper (None pour tous)
MAX_GENRES = 5

# Nombre maximum de films par genre et par période (None pour tous)
MAX_FILMS_PER_GENRE_PERIOD = 20

# Nombre maximum de films au total (None pour pas de limite)
MAX_TOTAL_FILMS = 100

# Nombre maximum de pages à parcourir par genre et période (None pour toutes)
MAX_PAGES_PER_GENRE_PERIOD = 3

# Configuration d'exportation
EXPORT_SETTINGS = {
    'FEED_URI': 'file:///home/l-o/Projets/film-prediction/scrappingJPBOX2/exports/jpbox_films_export.csv',
    'FEED_FORMAT': 'csv',
    'FEED_EXPORT_ENCODING': 'utf-8-sig',
    'FEED_EXPORT_DELIMITER': ';',
}

# Paramètres de performance
PERFORMANCE_SETTINGS = {
    'DOWNLOAD_DELAY': 1,
    'CONCURRENT_REQUESTS': 16,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
}

# Paramètres de logging
LOGGING_SETTINGS = {
    'LOG_LEVEL': 'INFO',
    'LOG_FILE': 'jpbox_scraping.log',
}

# Liste des genres spécifiques à scraper (laissez vide pour tous les genres)
# Exemple: ["Action", "Comédie", "Drame"]
SPECIFIC_GENRES = []

# Récupérer les acteurs principaux seulement (True) ou tous les acteurs (False)
MAIN_ACTORS_ONLY = True
# Nombre maximum d'acteurs à récupérer
MAX_ACTORS = 10

# Activer le mode debug (moins de films, plus de logs)
DEBUG_MODE = False

# Liste des champs à exporter
EXPORT_FIELDS = [
    'film_id', 'titre', 'genre_principale', 'genres', 'date_sortie_france', 
    'date_sortie_usa', 'duree_minutes', 'synopsis', 'realisateur', 'acteurs', 
    'pays_origine', 'budget', 'box_office_demarrage', 'box_office_france', 'recette_usa', 
    'recette_monde', 'image_url', 'note_moyenne'
]