from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union


class MovieInput(BaseModel):
    film_title: str
    release_date: str
    duration: str
    age_classification: Optional[str] = None
    producers: Optional[str] = None
    director: Optional[str] = None
    top_stars: Optional[str] = None
    languages: Optional[str] = None
    distributor: Optional[str] = None
    year_of_production: Optional[str] = None
    film_nationality: Optional[str] = None
    filming_secrets: Optional[str] = None
    awards: Optional[str] = None
    associated_genres: Optional[str] = None
    broadcast_category: Optional[str] = None
    trailer_views: Optional[str] = None
    synopsis: Optional[str] = None
    fr_entries: Optional[int] = 0  


class MovieFeatures(BaseModel):
    film_title: str
    film_url: Optional[str] = ''
    film_image_url: Optional[str] = ''
    release_date: Optional[str] = None
    duration: Optional[float] = None
    director: Optional[str] = None
    press_rating: Optional[float] = None
    viewer_rating: Optional[float] = None
    distributor: Optional[str] = None
    year_of_production: Optional[int] = None
    fr_entries: Optional[int] = 0
    us_entries: Optional[int] = 0
    budget: Optional[str] = None
    broadcast_category: Optional[str] = None
    synopsis: Optional[str] = None
    film_id: Optional[str] = None
    release_season: Optional[str] = None
    producers_list: Optional[List[str]] = None
    producers_count: Optional[int] = None
    top_stars_list: Optional[List[str]] = None
    top_stars_count: Optional[int] = None
    languages_list: Optional[List[str]] = None
    languages_count: Optional[int] = None
    nationality_list: Optional[List[str]] = None
    nationality_list_count: Optional[int] = None
    associated_genres_list: Optional[List[str]] = None
    associated_genres_count: Optional[int] = None
    fr_entry_week_iso_week: Optional[int] = None
    us_entry_week_iso_week: Optional[int] = None
    filming_secrets_num: Optional[int] = None
    press_critics_count_num: Optional[int] = None
    award_count: Optional[int] = None
    nomination_count: Optional[int] = None
    viewer_notes: Optional[int] = None
    viewer_critiques: Optional[int] = None
    trailer_views_num: Optional[float] = None
    synopsis_length: Optional[int] = None
    trailer_views_num_binary: Optional[int] = None
    duration_binary: Optional[int] = None
    press_rating_binary: Optional[int] = None
    viewer_rating_binary: Optional[int] = None
    year_of_production_binary: Optional[int] = None
    release_season_binary: Optional[int] = None
    broadcast_category_binary: Optional[int] = None
    release_date_binary: Optional[int] = None
    director_binary: Optional[int] = None
    synopsis_binary: Optional[int] = None
    distributor_binary: Optional[int] = None
    nationality_list_binary: Optional[int] = None
    producers_count_binary: Optional[int] = None
    top_stars_count_binary: Optional[int] = None


class MoviePrediction(BaseModel):
    film_title: str
    predicted_fr_entries: int
    features: Dict[str, Any] = None


class BatchMovieInput(BaseModel):
    movies: List[MovieInput]


class BatchMoviePrediction(BaseModel):
    predictions: List[MoviePrediction]