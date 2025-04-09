from sqlmodel import Session, select
from database_manager import get_engine
from typing import Optional
import pandas as pd

from csv_reader_base import BaseCsvReader
from csv_reader_allocine import AllocineCsvReader
from csv_reader_jp_box import JpBoxCsvReader

from models import Film, Person, Featuring, GeographicZone, Admissions, Recette
from expected_fields import CsvType, JpBoxExpectedFilmField, WikipediaPopulationFields, Country, AdmissionPeriod

#______________________________________________________________________________
class CSV2DataBase() :
    def __init__(self):
        self.jp_box_csv_filename = ('films_jp_box.csv')
        self.allocine_csv_filename = ('films_allocine.csv')
        self.wikipedia_populations = ('wikipedia_populations.csv')
        self.initialize_countries()

    #__________________________________________________________________________
    #
    #  region initialize countries
    #__________________________________________________________________________
    def initialize_countries(self):
        countries = pd.read_csv(self.wikipedia_populations, delimiter=',', quotechar='"')

        engine = get_engine()
        with Session(engine) as session:

            statement = select(GeographicZone)
            results = session.exec(statement).all()
            names = list(filter(lambda x: x.name, results))

            for line in countries.itertuples():
                current_country = str(getattr(line,WikipediaPopulationFields.COUNTRY.value))
                if current_country in names : 
                    continue

                current_population_str = getattr(line,WikipediaPopulationFields.POPULATION.value)
                current_population = int(current_population_str)
                new_zone = GeographicZone(
                    name = current_country, 
                    population = current_population
                )
                session.add(new_zone)
                try:
                    session.commit()
                except Exception as ex :
                    session.rollback()

    #__________________________________________________________________________
    #
    #  region load_data
    #__________________________________________________________________________
    def load_data(self, csvType:CsvType) -> pd.DataFrame:
        match csvType :
            case CsvType.JPBOX : data : pd.DataFrame = self.read_csv(self.jp_box_csv_filename)
            case CsvType.ALLOCINE : data : pd.DataFrame = self.read_csv(self.allocine_csv_filename)
        return data
    #__________________________________________________________________________
    #
    #  region read_csv
    #__________________________________________________________________________
    def read_csv(self, filename) -> pd.DataFrame:
        data = pd.read_csv(filename, delimiter=',', quotechar='"')
        return data
    
    #__________________________________________________________________________
    #
    #  region create_csv_reader
    #__________________________________________________________________________ 
    def create_csv_reader(self, csvType:CsvType ) -> BaseCsvReader: 
        match csvType :
            case CsvType.JPBOX : csv_reader = JpBoxCsvReader()
            case CsvType.ALLOCINE : csv_reader = AllocineCsvReader()
        return csv_reader
                    
    #__________________________________________________________________________
    #
    #  region fill_database
    #__________________________________________________________________________
    def fill_database(self, csv_type : CsvType) :
        dataframe = None
        dataframe = self.load_data(csv_type)
        if dataframe is None :
            return
        
        field_reference = dataframe.columns

        csv_reader = self.create_csv_reader(csv_type)
        csv_reader.check_columns(field_reference) 
  
        engine = get_engine()
        with Session(engine) as session:
            for line in dataframe.itertuples():
                csv_reader.read_csv_line(session, line)
      
                
    