from sqlmodel import Session, select
from typing import Optional, Iterable, Any
import pandas as pd

from csv_reader_base import BaseCsvReader
from expected_fields import AllocineExpectedFilmField, Country

from models import Film, Person, Featuring, GeographicZone, Admissions, Recette

class AllocineCsvReader(BaseCsvReader):  

    def __init__(self):
        pass

    #__________________________________________________________________________
    #
    #  region check_columns
    #__________________________________________________________________________
    def check_columns(self, csv_fields):
        expected_fields = [x.value for x in AllocineExpectedFilmField ]
        return super().check_columns(csv_fields, expected_fields)
    
    #__________________________________________________________________________
    #
    #  region read_csv_line
    #__________________________________________________________________________
    def read_csv_line(self, session : Session, line : Iterable[Any]):
        pass

    