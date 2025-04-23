from enum import Enum

class DataType(Enum) :
    UNDEFINED = 0
    JP_POX_FILMS = 1
    FUSION_V3 = 2 
    ALLOCINE_INCREMENT = 3

from .models import Movie, PredictionHistory, INITIAL_DATE_FORMAT_STRING, ALLOCINE_DATE_FORMAT_STRING, ALLOCINE_DATE_FORMAT_STRING2
import datetime as dt
import locale
from typing import Sequence

class DataImporter() :
    def __init__(self) :
        self.data_type = DataType.UNDEFINED

    def set_column_names(self, column_names: Sequence[str]):
        print(f"Colonnes détectées: {column_names}")  # Ajoutez cette ligne pour le débogage
    
        if 'film_title' in column_names and 'associated_genres' in column_names:
            self.data_type = DataType.ALLOCINE_INCREMENT
            print("Format détecté: ALLOCINE_INCREMENT")
            return

        self.data_type = DataType.UNDEFINED
     

    def try_import_row(self, row: dict) -> bool:
        print(f"Traitement de la ligne: {row}")  # Débogage
        str_title = "no title"
        release_date_france = dt.datetime.now()
        
        try:
            # Déterminer le titre
            match self.data_type:
                case DataType.JP_POX_FILMS: 
                    str_title = str(row['titre'])
                case DataType.FUSION_V3: 
                    str_title = str(row['titre_jpbox'])
                case DataType.ALLOCINE_INCREMENT:
                    # Adaptez à votre CSV
                    str_title = str(row.get('film_title', row.get('titre', 'no title')))
                case _: 
                    raise Exception('Unable to find title column')

            # Déterminer la date de sortie
            match self.data_type:
                case DataType.JP_POX_FILMS: 
                    release_date_france = dt.datetime.strptime(row['date_sortie_france'], INITIAL_DATE_FORMAT_STRING)
                case DataType.FUSION_V3: 
                    release_date_france = dt.datetime.strptime(row['date_sortie_france'], INITIAL_DATE_FORMAT_STRING)
                case DataType.ALLOCINE_INCREMENT: 
                    try:
                        release_date_france = CustomDate().parse_french_date(row['release_date'])
                    except Exception as e:
                        print(f"Erreur de parsing de date: {e}")
                        # Utiliser une date par défaut ou actuelle si le parsing échoue
                        release_date_france = dt.datetime.now()
                case _: 
                    raise Exception('Unable to find release_date_france column')
        
        except Exception as e:
            print(f"Error reading movie title and release date: {str_title}, {e}")
            return False

    # Le reste de votre code...
        
    
class CustomDate():
    def __init__(self) :
        self.mois_fr = {
                'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
                'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
            }

    def parse_french_date(self, date_str: str) -> dt.datetime:
        date_str = date_str.strip().lower()
        parts = date_str.split()

        try:
            if len(parts) == 3:  # ex: "7 août 2024"
                day = int(parts[0])
                month = self.mois_fr[parts[1]]
                year = int(parts[2])
            elif len(parts) == 2:  # ex: "août 2024"
                day = 1
                month = self.mois_fr[parts[0]]
                year = int(parts[1])
            elif len(parts) == 1:  # ex: "2024"
                day = 1
                month = 1
                year = int(parts[0])
            else:
                raise ValueError("Format de date non reconnu")
            
            return dt.datetime(year, month, day)
        
        except Exception as e:
            raise ValueError(f"Erreur lors du parsing de la date '{date_str}': {e}")
