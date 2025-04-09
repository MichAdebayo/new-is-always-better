from sqlmodel import Session, select
from typing import Optional, Iterable, Any
import pandas as pd

from csv_reader_base import BaseCsvReader
from expected_fields import JpBoxExpectedFilmField

from models import Film, Person, Featuring, GeographicZone, Admissions, Recette
from expected_fields import CsvType, JpBoxExpectedFilmField, WikipediaPopulationFields, Country, AdmissionPeriod

class JpBoxCsvReader(BaseCsvReader):  
    def __init__(self):
        pass
    #__________________________________________________________________________
    #
    #  region check_columns
    #__________________________________________________________________________
    def check_columns(self, csv_fields):
        expected_fields = [x.value for x in JpBoxExpectedFilmField ]
        return super().check_columns(csv_fields, expected_fields)
    
    #__________________________________________________________________________
    #
    #  region read_csv_line
    #__________________________________________________________________________
    def read_csv_line(self, session : Session, line : Iterable[Any]):

        super().read_csv_line(session, line)

        jp_box_id = int(getattr(line, JpBoxExpectedFilmField.JPBOX_ID.value ))
        title = str(getattr(line,JpBoxExpectedFilmField.TITLE.value))
        genre = str(getattr(line,JpBoxExpectedFilmField.GENRE.value))
        france_release_date = str(getattr(line,JpBoxExpectedFilmField.FRANCE_RELEASE_DATE.value))
        usa_release_date  = str(getattr(line, JpBoxExpectedFilmField.USA_RELEASE_DATE.value))
        average_note =  str(getattr(line, JpBoxExpectedFilmField.AVERAGE_NOTE.value))
        featuring = str(getattr(line, JpBoxExpectedFilmField.FEATURING.value))
            
        france_first_week_admissions_str = getattr(line, JpBoxExpectedFilmField.FRANCE_FIRST_WEEK.value)
        france_total_admissions_str = getattr(line, JpBoxExpectedFilmField.FRANCE_TOTAL.value)
        
        budget_str = str(getattr(line, JpBoxExpectedFilmField.BUDGET.value))
        usa_recette_str = getattr(line, JpBoxExpectedFilmField.USA_RECETTE.value)
        not_usa_recette_str = getattr(line, JpBoxExpectedFilmField.NO_USA_RECETTE.value)
        world_recette_str = getattr(line, JpBoxExpectedFilmField.WORLD_RECETTE.value)

        image_url  = str(getattr(line,JpBoxExpectedFilmField.IMAGE_URL.value))
        description = str(getattr(line,JpBoxExpectedFilmField.DESCRIPTION.value))
        duration = str(getattr(line,JpBoxExpectedFilmField.DURATION.value))

        film = super().create_or_update_film(session, 
            title, 
            genre, duration, description, 
            budget_str, 
            france_release_date, usa_release_date,
            jp_box_id)
        
        if film != None :
            self.add_jpbox_actors_to_session(session, film, featuring)

            admis_fra_first = super().create_or_update_admissions(session, film, Country.FRANCE, france_release_date,  AdmissionPeriod.FIRST_WEEK, france_first_week_admissions_str)
            admis_fra_total = super().create_or_update_admissions(session, film, Country.FRANCE, france_release_date,  AdmissionPeriod.TOTAL, france_total_admissions_str)

            self.add_jpbox_recette(session, film, Country.WORLD, world_recette_str)
            self.add_jpbox_recette(session, film, Country.USA, usa_recette_str)
            calcul_is_correct = self.verif_jpbox_recette(world_recette_str, not_usa_recette_str, usa_recette_str)

    #__________________________________________________________________________
    #
    #  region add_jpbox_actors_to_session
    #__________________________________________________________________________
    def add_jpbox_actors_to_session(self, session : Session, film: Film, featuring : str):
        actors = featuring. split('|')

        for actor in actors :
            actor_datas = actor.split('(')
            actor_name = actor_datas[0].strip()
            if len(actor_datas) > 1 :
                actor_data = actor_datas[1].replace(')','')
                role = actor_data.split('-')[0].strip()
            else :
                role = "NotParsed"
         
            statement = select(Person).where(Person.full_name == actor_name)
            result = session.exec(statement).one_or_none()
            if result != None :
                person = result
            else :
                person = Person(full_name = actor_name)
                session.add(person)
                try:
                    session.commit()
                except Exception as ex :
                    session.rollback()

            session.refresh(person)

            statement = select(Featuring).where(Featuring.film_id == film.id)
            results = session.exec(statement).all()

            existing_featuring = False
            for featuring_line in results :
                if featuring_line.film_id != film.id : break
                if featuring_line.person_id != person.id : break
                if featuring_line.role != role : break
                existing_featuring = True

            if not existing_featuring : 
                new_featuring = Featuring(
                    film_id = film.id,
                    person_id=person.id,
                    role = role
                )
                session.add(new_featuring)
                try:
                    session.commit()
                except Exception as ex :
                    session.rollback()
        
    #__________________________________________________________________________
    #
    #  region add_jpbox_recette
    #__________________________________________________________________________
    def add_jpbox_recette(self, session : Session, film_id : int, geographic_zone_str :str, recette_str:str):
        statement = select(Recette).where(Recette.film_id==film_id).where(Recette.geographic_zone.name == geographic_zone_str)
        result = session.exec(statement).one_or_none()
        
        if result == None :
            zone = self.get_zone(session, geographic_zone_str)
            if zone == None : 
                return None
            
        recette_value = super().cast_from_dollar(recette_str) 
        if recette_value!= 0 :
            recette = Recette(
                film_id==film_id, 
                geographic_zone=zone.id,
                recette_in_dollars=recette_value
            )
            session.add(recette)
            try:
                session.commit()
            except Exception as ex :
                session.rollback()

    def verif_jpbox_recette(self, world_recette_str:str, not_usa_recette_str:str, usa_recette_str:str):
        world_recette_value = super().cast_from_dollar(world_recette_str)
        not_usa_recette_value = super().cast_from_dollar(not_usa_recette_str)
        usa_recette_value = super().cast_from_dollar(usa_recette_str)

        if not_usa_recette_value == (world_recette_value - usa_recette_value) :
            return True
        else :
            return False



        
            