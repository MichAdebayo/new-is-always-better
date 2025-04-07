from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Film(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    jp_box_id : int = Field(default=None) 
    title: str
  
    usa_release_date : Optional[str] = None
    france_release_date: Optional[str] = None
    france_first_week_admissions : Optional[int] = None
    
    genre: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    image_url : Optional[str] = None
    
    # Relation avec la table Featuring
    people: List["Featuring"] = Relationship(back_populates="film")


class Person(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    full_name: str
    birth_date: Optional[str] = None
    biography: Optional[str] = None

    # Relation avec la table Featuring
    roles: List["Featuring"] = Relationship(back_populates="person")


class Featuring(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    person_id: int = Field(foreign_key="person.id")
    film_id: int = Field(foreign_key="film.id")
    role: str

    # Relations avec les tables film et person
    person: "Person" = Relationship(back_populates="roles")
    film: "Film" = Relationship(back_populates="people")