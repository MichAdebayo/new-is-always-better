from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Film(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    jp_box_id : Optional[int] = Field(default=None) 
    allocine_id : Optional[int] = Field(default=None) 
    title: str
    
    genre: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    page_url : Optional[str] = None
    image_url : Optional[str] = None
    budget_in_dollar : Optional[int] = None
    
    # Relation with featuring and admissions tables
    featuring: List["Featuring"] = Relationship(back_populates="film")
    admissions : List["Admissions"] = Relationship(back_populates="film")
    recettes: List["Recette"] = Relationship(back_populates="film")

class Person(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    full_name: str
    birth_date: Optional[str] = None
    biography: Optional[str] = None

    # Relation with featuring table
    roles: List["Featuring"] = Relationship(back_populates="person")

class Featuring(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    film_id: int = Field(foreign_key="film.id")
    person_id: int = Field(foreign_key="person.id")
    role: str

    # Relation with film and person tables
    film: "Film" = Relationship(back_populates="featuring")
    person: "Person" = Relationship(back_populates="roles")

class GeographicZone(SQLModel, table=True):
    __tablename__= "geographic_zone"
    id: int = Field(default=None, primary_key=True)
    name : Optional[str] 
    population : Optional[str]

    # Relation with admissions table
    #admissions: List["Admissions"] = Relationship(back_populates="geographic_zone")

class Admissions(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    film_id: int = Field(foreign_key="film.id")
    geographic_zone_id: int = Field(foreign_key="geographic_zone.id")
    release_date : Optional[str] = None
    period : Optional[str] = None
    number : Optional[int] = None

    # Relations with film and geographic_zone tables
    film: "Film" = Relationship(back_populates="admissions")
    #geographic_zone: "GeographicZone" = Relationship(back_populates="admissions")

class Recette(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    film_id : int = Field(foreign_key="film.id")
    geographic_zone_id: int = Field(foreign_key="geographic_zone.id")
    recette_in_dollars : Optional[int] 

    # Relations with film and geographic_zone tables
    film: "Film" = Relationship(back_populates="recettes")
    #geographic_zone: "GeographicZone" = Relationship(back_populates="recette")

    