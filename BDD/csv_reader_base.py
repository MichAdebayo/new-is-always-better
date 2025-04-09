from sqlmodel import Session, select
from typing import Optional, Iterable, Any
import pandas as pd

from models import Film, Person, Featuring, GeographicZone, Admissions, Recette
from expected_fields import CsvType, Country, AdmissionPeriod

class BaseCsvReader():

    def __init__(self):
        self.fra_zone_id = 0
        self.usa_zone_id = 0
    #__________________________________________________________________________
    #
    #  region check_columns
    #__________________________________________________________________________
    def check_columns(self, csv_fields : pd.Index, expected_fields :list[str]) :
        for csv_field in csv_fields : 
            if csv_field  not in expected_fields :
                raise Exception(f"{csv_field} is not present in expected_fields")
            
    #__________________________________________________________________________
    #
    #  region get_zone
    #__________________________________________________________________________
    def get_zone(self, session : Session, country : str) -> GeographicZone :

        statement = select(GeographicZone).where(GeographicZone.name == country)
        result = session.exec(statement)
        zones = result.all()
        if len(zones) >0 :
            return zones[0]
        
        raise Exception(f"Unknown geographic zone : {country}")
    
    #__________________________________________________________________________
    #
    #  region read_csv_line
    #__________________________________________________________________________
    def read_csv_line(self, session : Session, line : Iterable[Any]):
        self.fra_zone_id = self.get_zone(session, Country.FRANCE.value).id
        self.usa_zone_id = self.get_zone(session, Country.USA.value).id

    #__________________________________________________________________________
    #
    #  region create_or_update_film
    #__________________________________________________________________________
    def create_or_update_film(self, session: Session, 
        title : str, genre: str, duration: str, description: str,
        budget_str: str,
        release_date_fr : Optional[str],
        release_date_us : Optional[str],
        jp_box_id : Optional[int],
        allocine_id : Optional[int]) -> Optional[Film] :

        statement = select(Film, Admissions).where(Film.title==title)
        results = session.exec(statement).all()

        found_film = None

        for (film, admissions) in results :
            for film_admissions in film.admissions :
                match film_admissions.geographic_zone_id :
                    case self.fra_zone_id : 
                        if film_admissions.release_date == release_date_fr :
                            found_film = film

                    case self.usa_zone_id :
                        if film_admissions.release_date == release_date_us :
                            found_film = film

            if found_film != None : 
                break

        budget_value = self.cast_from_dollar(budget_str)

        if found_film :
            film = found_film
            film.genre += genre
            film.duration += duration
            film.description += description
            if film.budget_in_dollar ==0 : film.budget_in_dollar = budget_value

        else : 
            film = Film(
                title = title,
                genre = genre,
                duration = duration,
                description = description, 
                budget_in_dollar = budget_value
            )


        if jp_box_id : found_film.jp_box_id = jp_box_id
        if allocine_id : found_film.allocine_id = jp_box_id

        session.add(film)
        try:
            session.commit()
            session.refresh(film)
            return film
        
        except Exception as ex :
            session.rollback()
            
        return None
    
    #__________________________________________________________________________
    #
    #  region create_or_update_admissions
    #__________________________________________________________________________
    def create_or_update_admissions(self, session : Session, film: Film, 
        country : str, 
        start_date :str, 
        admission_period : AdmissionPeriod, admissions_value:str) -> Optional[Admissions]:

        zone = self.get_zone(session, country)
        
        admissions_value = admissions_value.replace(" ", "")
        admissions_number = int(admissions_value) if isinstance(admissions_value, int) else None

        statement = select(Admissions).where(Admissions.film_id == film.id)
        results = session.exec(statement).all()

        existing_admissions = False
        for admissions_line in results :
            if admissions_line.film_id != film.id : break
            if admissions_line.geographic_zone.id != zone.id : break
            if admissions_line.period != admission_period.value : break
            existing_admissions = True

        if not existing_admissions : 
            new_admissions = Admissions(
                film_id = film.id,
                release_date= start_date,
                period=admission_period.value , 
                number = admissions_number 
            )
            session.add(new_admissions)
            try:
                session.commit()
                session.refresh(new_admissions)
                return new_admissions
            
            except Exception as ex :
                session.rollback()
        
        return None
    
    #__________________________________________________________________________
    #
    #  region cast_from_dollar
    #__________________________________________________________________________
    def cast_from_dollar(self, readt_str: str) -> int :
        money_value = readt_str.replace('$', '').replace(' ', '')
        if isinstance(money_value, int) :
            money_value : int = int(money_value)
            return money_value
        else : 
            raise Exception(f"Impossible to cast value in dollar : {readt_str}")
    
    

  


        

    