# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv
import os
from datetime import datetime

class ScrappingjpboxPipeline:
    def __init__(self):
        self.file = None
        self.csv_writer = None
        self.count = 0
        self.filename = f"jpbox_films_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    def open_spider(self, spider):
        # Créer le répertoire d'exports s'il n'existe pas
        if not os.path.exists('exports'):
            os.makedirs('exports')
        
        # Ouvrir le fichier CSV
        self.file = open(f'exports/{self.filename}', 'w', newline='', encoding='utf-8-sig')
        
        # Définir les champs à exporter
        fieldnames = [
            'film_id', 'titre', 'genre_principale', 'genres', 'date_sortie_france', 
            'date_sortie_usa', 'duree_minutes', 'synopsis', 'realisateur', 'acteurs', 
            'pays_origine', 'budget', 'box_office_demarrage','box_office_france', 'recette_usa', 
            'recette_monde', 'image_url', 'note_moyenne'
        ]
        
        # Créer le writer CSV
        self.csv_writer = csv.DictWriter(self.file, fieldnames=fieldnames, delimiter=';')
        self.csv_writer.writeheader()
        
        spider.logger.info(f"Pipeline initialisé - Fichier de sortie: exports/{self.filename}")
    
    
    def process_item(self, item, spider):
        # Convertir l'item en dictionnaire
        item_dict = ItemAdapter(item).asdict()
        
        # S'assurer que toutes les clés existent (avec valeurs par défaut si absentes)
        for field in self.csv_writer.fieldnames:
            if field not in item_dict:
                item_dict[field] = ""
        
        # Nettoyer les valeurs pour éviter les problèmes d'encodage et de délimitation
        for key, value in item_dict.items():
            if value is None:
                item_dict[key] = ""
            elif isinstance(value, str):
                if key == 'synopsis':
                    # Traitement spécial pour le synopsis qui peut contenir du texte complexe
                    # Remplacer les retours à la ligne, les points-virgules, et échapper les guillemets
                    clean_value = value.replace('\n', ' ').replace('\r', ' ')
                    clean_value = clean_value.replace(';', ',')
                    clean_value = clean_value.replace('"', '""')  # Double les guillemets pour les échapper en CSV
                    item_dict[key] = clean_value
                else:
                    # Pour les autres champs textuels
                    clean_value = value.replace('\n', ' ').replace('\r', ' ')
                    clean_value = clean_value.replace(';', ',')
                    item_dict[key] = clean_value
        
        # Écrire la ligne dans le CSV avec gestion d'erreur
        try:
            self.csv_writer.writerow(item_dict)
            self.file.flush()  # Force l'écriture immédiate pour éviter la perte de données
            
            # Incrémenter le compteur et afficher un log
            self.count += 1
            if self.count % 10 == 0:  # Log plus fréquent (tous les 10 items)
                spider.logger.info(f"Extraction en cours: {self.count} films traités")
                
        except Exception as e:
            # Log détaillé en cas d'erreur d'écriture
            spider.logger.error(f"ERREUR d'écriture CSV pour '{item_dict.get('titre', 'inconnu')}': {e}")
            # Tenter d'identifier la valeur problématique
            for k, v in item_dict.items():
                if isinstance(v, str) and len(v) > 100:  # Vérifier les champs longs
                    spider.logger.debug(f"Champ potentiellement problématique {k}: {v[:50]}...")
        
        return item