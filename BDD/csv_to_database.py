from sqlmodel import Session
from database_manager import get_engine
from models import Film, Person, Featuring
import pandas as pd

from enum import StrEnum


#______________________________________________________________________________
#
#  region champ Leo :
#  film_id, titre,genre_principale,
#  date_sortie_france,date_sortie_usa,
#  image_url,synopsis,
#  duree,
#  note_moyenne,
#  acteurs,
#  entrees_demarrage_france,
#  entrees_totales_france,
#  budget,recette_usa,recette_reste_du_monde,recette_monde
#______________________________________________________________________________
class CsvExpectedFilmField(StrEnum) :
    JPBOX_ID = "film_id"
    TITLE = "titre"
    GENRE = "genre_principale"
    FRANCE_RELEASE_DATE = "date_sortie_france"
    USA_RELEASE_DATE = "date_sortie_usa"
    IMAGE_URL = "image_url"
    DESCRIPTION = "synopsis"
    DURATION = "duree"
    AVERAGE_NOTE = "note_moyenne"
    FEATURING = "acteurs"
    FRANCE_FIRST_WEEK = "entrees_demarrage_france"
    FRANCE_TOTAL = "entrees_totales_france"
    BUDGET = "budget"
    USA_RECETTE = "recette_usa"
    NO_USA_RECETTE = "recette_reste_du_monde"
    WORLD_RECETTE = "recette_monde"


class CSV2DataBase() :
    def __init__(self):
        pass

    def load_data(self) -> pd.DataFrame:
        data : pd.DataFrame = self.read_csv()
        return data

    def read_csv(self) -> pd.DataFrame:
        data = pd.read_csv('films.csv', delimiter=',', quotechar='"')
        return data
    
    def check_columns(self, csv_fields : pd.Index) :
        expected_fields = [x.value for x in CsvExpectedFilmField ]
        for csv_field in csv_fields : 
            if csv_field  not in expected_fields :
                raise Exception(f"{csv_field} is not present in expected_fields")

    def fill_database(self) :
        dataframe = None
        dataframe = self.load_data()
        if dataframe is None :
            return

        field_reference = dataframe.columns
        self.check_columns(field_reference) 
  
        engine = get_engine()
        with Session(engine) as session:
            for line in dataframe.itertuples():

                jp_box_id = int(getattr(line, CsvExpectedFilmField.JPBOX_ID.value ))
                title = str(getattr(line,CsvExpectedFilmField.TITLE.value))
                genre = str(getattr(line,CsvExpectedFilmField.GENRE.value))
                france_release_date = str(getattr(line,CsvExpectedFilmField.FRANCE_RELEASE_DATE.value))
                usa_release_date  = str(getattr(line, CsvExpectedFilmField.USA_RELEASE_DATE.value))
                average_note =  str(getattr(line, CsvExpectedFilmField.AVERAGE_NOTE.value))
                featuring = str(getattr(line, CsvExpectedFilmField.FEATURING.value))
                    
                france_first_week_admissions_value = getattr(line, CsvExpectedFilmField.FRANCE_FIRST_WEEK.value)
                france_first_week_admissions = int(france_first_week_admissions_value) if isinstance(france_first_week_admissions_value, int) else None

                france_total_admissions_value = getattr(line, CsvExpectedFilmField.FRANCE_TOTAL.value)
                
                budget = getattr(line, CsvExpectedFilmField.BUDGET.value)
                usa_recette = getattr(line, CsvExpectedFilmField.USA_RECETTE.value)
                not_usa_recette = getattr(line, CsvExpectedFilmField.NO_USA_RECETTE.value)
                world_recette = getattr(line, CsvExpectedFilmField.WORLD_RECETTE.value)

                image_url  = str(getattr(line,CsvExpectedFilmField.IMAGE_URL.value))
                description = str(getattr(line,CsvExpectedFilmField.DESCRIPTION.value))
                duration = str(getattr(line,CsvExpectedFilmField.DURATION.value))

                film = Film(
                     jp_box_id = jp_box_id,
                     title = title,
                     usa_release_date = usa_release_date, 
                     france_release_date = france_release_date,
                     france_first_week_admissions = france_first_week_admissions,
                     genre = genre,
                     duration = duration,
                     description = description
                )
                session.add(film)

                try:
                    session.commit()
                except Exception as ex :
                    session.rollback()
            