from enum import Enum

class DataType(Enum) :
    UNDEFINED = 0
    JP_POX_FILMS = 1
    FUSION_V3 = 2 
    ALLOCINE_INCREMENT = 3

from .models import Movie, PredictionHistory, INITIAL_DATE_FORMAT_STRING, ALLOCINE_DATE_FORMAT_STRING
import datetime as dt
import locale
from typing import Sequence

class DataImporter() :
    def __init__(self) :
        self.data_type = DataType.UNDEFINED

    def set_column_names(self, column_names: Sequence[str]) :
        if 'genre_principale' in column_names :
            if 'titre' in column_names : 
                self.data_type = DataType.JP_POX_FILMS
                return 

            if 'titre_jpbox' in column_names :
                self.data_type = DataType.FUSION_V3
                return

        if 'film_title' in column_names:
            if 'associated_genres' in column_names:
                self.data_type = DataType.ALLOCINE_INCREMENT
                # Définir la locale en français (à adapter selon ton OS)
                locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Linux / macOS
                # locale.setlocale(locale.LC_TIME, 'French_France.1252')  # Windows
                return

        self.data_type = DataType.UNDEFINED
     

    def try_import_row(self, row : dict) -> bool:
        #print(row)  # Affiche les données de chaque ligne
        str_title = "no title"
        release_date_france = dt.datetime.now()
        try:
            
            match self.data_type:
                case DataType.JP_POX_FILMS : str_title = str(row['titre'])
                case DataType.FUSION_V3 : str_title = str(row['titre_jpbox'])
                case DataType.ALLOCINE_INCREMENT : str_title = str(row['film_title'])
                case _ : raise Exception('Unable to find title column')

            match self.data_type:
                case DataType.JP_POX_FILMS : release_date_france = dt.datetime.strptime(row['date_sortie_france'], INITIAL_DATE_FORMAT_STRING)
                case DataType.FUSION_V3 : release_date_france = dt.datetime.strptime(row['date_sortie_france'], INITIAL_DATE_FORMAT_STRING)
                case DataType.ALLOCINE_INCREMENT : release_date_france = dt.datetime.strptime(row['release_date'], ALLOCINE_DATE_FORMAT_STRING)
                case _ : raise Exception('Unable to find release_date_france column')
        
        except :
            print(f"Error reading movie title and release date : {str_title}, {release_date_france}")
            return False

        updating_movie = None
        try :

            updating_movie = Movie.objects.filter( 
                title = str_title, 
                release_date_fr = release_date_france
            )
            results= list(updating_movie)
            updating_movie = None
            if len(results) !=0 :
                updating_movie : Movie = results[0]
            
            match self.data_type:
                case DataType.JP_POX_FILMS : str_image_url = str(row['image_url'])
                case DataType.FUSION_V3 : str_image_url = str(row['image_url'])
                case DataType.ALLOCINE_INCREMENT : str_image_url = str(row['film_image_url'])
                case _ : raise Exception('Unable to find image_url column')

            match self.data_type:
                case DataType.JP_POX_FILMS : str_synopsis = str(row['synopsis'])
                case DataType.FUSION_V3 : str_synopsis = str(row['synopsis'])
                case DataType.ALLOCINE_INCREMENT : str_synopsis = str(row['synopsis'])
                case _ : raise Exception('Unable to find synopsis column')

            match self.data_type:
                case DataType.JP_POX_FILMS : str_genre = str(row['genre_principale'])
                case DataType.FUSION_V3 : str_genre = str(row['genre_principale'])
                case DataType.ALLOCINE_INCREMENT : str_genre = str(row['associated_genres'])
                case _ : raise Exception('Unable to find genre(s) column')

            match self.data_type:
                case DataType.JP_POX_FILMS : str_cast = str(row['acteurs'])
                case DataType.FUSION_V3 : str_cast = str(row['acteurs'])
                case DataType.ALLOCINE_INCREMENT : str_cast = str(row['top_stars'])
                case _ : raise Exception('Unable to find cast column')

            match self.data_type:
                case DataType.JP_POX_FILMS : real_entries_str = str(row['entrees_demarrage_france']).replace(' ', '')
                case DataType.FUSION_V3 : real_entries_str = str(row['entrees_demarrage_france']).replace(' ', '')
                case DataType.ALLOCINE_INCREMENT : real_entries_str = str(row['fr_entries']).replace(' ', '')
                case _ : raise Exception('Unable to find cast column')

            real_entries = 0 
            try :
                real_entries =  int(real_entries_str) 
            except : 
                pass
            
            if updating_movie :
                updating_movie.genre = str_image_url
                updating_movie.synopsis = str_synopsis
                updating_movie.genre = str_genre
                updating_movie.cast = str_cast
                updating_movie.first_week_actual_entries_france = real_entries
                updating_movie.save()
            else : 
                movie = Movie(
                    title = str_title,
                    image_url = str_image_url,
                    synopsis= str_synopsis,
                    genre = str_genre,
                    cast = str_cast, 
                    first_week_actual_entries_france = real_entries, 
                    release_date_fr = release_date_france
                )
                movie.save()
            return True

        except Exception as movie_error:
            print(f"Error inserting movie : {str_title}, {release_date_france}")
            return False
