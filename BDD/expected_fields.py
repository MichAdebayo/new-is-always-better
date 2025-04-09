from enum import Enum, StrEnum

class CsvType(Enum):
    JPBOX = 0
    ALLOCINE = 1

#______________________________________________________________________________
#
#  region champs JP BOX :
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
class JpBoxExpectedFilmField(StrEnum) :
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

#______________________________________________________________________________
#
#  region champs ALLOCINE :
#  film_title, film_url,film_image_url,
#  release_date, duration, age_classification,
#  producers, director, top_stars,
#  press_rating, viewer_rating,
#  languages, distributor,
#  year_of_production,
#  film_nationality,
#  filming_secrets,
#  fr_entry_week,
#  us_entry_week,
#  fr_entries,
#  us_entries,
#  awards,
#  budget,
#  associated_genres,
#  synopsis
#______________________________________________________________________________
class AllocineExpectedFilmField(StrEnum) :
    TITLE = "film_title"
    FILM_URL = "film_url"
    IMAGE_URL="film_image_url"
    RELEASE_DATE = "release_date"
    DURATION ="duration"
    AGE_CLASSIFICATION = "age_classification"
    PRODUCERS = "producers"
    DIRECTOR = "director"
    TOP_STARS = "top_stars"
    PRESS_RATING= "press_rating"
    VIEWER_RATING ="viewer_rating"
    LANGAGES = "languages"
    DISTRIBUTOR = "distributor"
    PRODUCTION_YEAR = "year_of_production"
    NATIONALITY = "film_nationality"
    SECRETS = "filming_secrets"
    FRANCE_FIRST_WEEK = "fr_entry_week"
    USA_FIRST_WEEK = "us_entry_week"
    FRANCE_TOTAL = "fr_entries"
    USA_TOTAL = "us_entries"
    AWARDS = "awards"
    BUDGET = "budget"
    ASSOCIATED_GENRES ="associated_genres"
    SYNOPSY="synopsis"

class WikipediaPopulationFields(StrEnum) :
    COUNTRY = "Pays"
    POPULATION = "Population_2025"

class Country(StrEnum) :
    FRANCE = "France"
    USA = "États-Unis"
    WORLD = "Monde"

class AdmissionPeriod(StrEnum) :
    FIRST_WEEK = "first_week"
    TOTAL = "total"