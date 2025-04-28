#movie_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union


class MovieInput(BaseModel):
    film_title: str
    release_date: str
    duration: Optional[str]= None
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

    fr_entries: Optional[int] = None
    duration: Optional[float] = None
    synopsis_length: Optional[float] = None
    award_count: Optional[float] = None
    nomination_count: Optional[float] = None
    trailer_views_num: Optional[float] = None
    filming_secrets_num: Optional[float] = None
    top_distributor_score: Optional[float] = None
    distributor_power: Optional[float] = None
    franchise_blockbuster_score: Optional[float] = None
    estimated_marketing_power: Optional[float] = None
    year_of_production: Optional[str] = None
    release_date_france_year: Optional[str] = None
    release_date_france_day: Optional[str] = None
    release_season: Optional[str] = None
    broadcast_category: Optional[str] = None
    duration_binary: Optional[int] = None
    director_binary: Optional[int] = None
    producers_count_binary: Optional[int] = None
    top_stars_count_binary: Optional[int] = None
    press_rating_binary: Optional[int] = None
    nationality_list_binary: Optional[int] = None
    viewer_rating_binary: Optional[int] = None
    trailer_views_num_binary: Optional[int] = None
    synopsis_binary: Optional[int] = None
    distributor_binary: Optional[int] = None
    duration_classified: Optional[str] = None
    synopsis_sentiment: Optional[float] = None
    is_sequel: Optional[int] = None
    synopsis_length_categorized: Optional[str] = None
    synopisis_sentiment_categorized: Optional[str] = None
    award_binary: Optional[int] = None
    nomination_binary: Optional[int] = None
    is_gaming_franchise: Optional[int] = None
    franchise_level: Optional[int] = None
    is_superhero_franchise: Optional[int] = None
    is_animation_franchise: Optional[int] = None
    is_action_franchise: Optional[int] = None
    is_licence: Optional[int] = None
    is_mcu: Optional[int] = None
    is_likely_blockbuster: Optional[int] = None
    is_major_studio: Optional[int] = None
    is_french_major_studio: Optional[int] = None
    major_studio_and_licence: Optional[int] = None
    french_major_and_licence: Optional[int] = None
    major_studio_x_franchise: Optional[int] = None
    is_connected_universe: Optional[int] = None
    film_title: Optional[str] = None
    director: Optional[str] = None
    distributor: Optional[str] = None
    lang_ARABIC: Optional[int] = None
    lang_Allemand: Optional[int] = None
    lang_Anglais: Optional[int] = None
    lang_Chinois: Optional[int] = None
    lang_Espagnol: Optional[int] = None
    lang_Français: Optional[int] = None
    lang_Hébreu: Optional[int] = None
    lang_Italien: Optional[int] = None
    lang_Japonais: Optional[int] = None
    lang_Latin: Optional[int] = None
    lang_Mandarin: Optional[int] = None
    lang_Portugais: Optional[int] = None
    lang_Russe: Optional[int] = None
    nat_Allemagne: Optional[int] = None
    nat_Australie: Optional[int] = None
    nat_Belgique: Optional[int] = None
    nat_Canada: Optional[int] = None
    nat_Espagne: Optional[int] = None
    nat_France: Optional[int] = None
    #rename
    nat_Grande_Bretagne: Optional[int] = None
    nat_Italie: Optional[int] = None
    nat_Japon: Optional[int] = None
    #rename
    nat_Nouvelle_Zélande: Optional[int] = None
    #rename
    nat_U_S_A_: Optional[int] = None
    star_André_Dussollier: Optional[int] = None
    star_Benoît_Poelvoorde: Optional[int] = None
    star_Brad_Pitt: Optional[int] = None
    star_Chris_Evans: Optional[int] = None
    star_Chris_Pratt: Optional[int] = None
    star_Christian_Clavier: Optional[int] = None
    star_Clovis_Cornillac: Optional[int] = None
    star_Daniel_Craig: Optional[int] = None
    star_Daniel_Radcliffe: Optional[int] = None
    star_Dany_Boon: Optional[int] = None
    star_Dwayne_Johnson: Optional[int] = None
    star_Emma_Watson: Optional[int] = None
    star_Ewan_McGregor: Optional[int] = None
    star_Franck_Dubosc: Optional[int] = None
    star_Gad_Elmaleh: Optional[int] = None
    star_George_Clooney: Optional[int] = None
    star_Gilles_Lellouche: Optional[int] = None
    star_Guillaume_Canet: Optional[int] = None
    star_Gérard_Depardieu: Optional[int] = None
    star_Gérard_Lanvin: Optional[int] = None
    star_Hugh_Jackman: Optional[int] = None
    star_Isabelle_Nanty: Optional[int] = None
    star_Jamel_Debbouze: Optional[int] = None
    star_Jason_Statham: Optional[int] = None
    star_Jean_Dujardin: Optional[int] = None
    star_Jean_Reno: Optional[int] = None
    #rename
    star_Jean_Paul_Rouve: Optional[int] = None
    star_Johnny_Depp: Optional[int] = None
    star_José_Garcia: Optional[int] = None
    star_Kad_Merad: Optional[int] = None
    star_Keira_Knightley: Optional[int] = None
    star_Kristen_Stewart: Optional[int] = None
    star_Leonardo_DiCaprio: Optional[int] = None
    star_Marion_Cotillard: Optional[int] = None
    star_Mark_Ruffalo: Optional[int] = None
    star_Matt_Damon: Optional[int] = None
    #rename
    star_Robert_Downey_Jr: Optional[int] = None
    star_Robert_Pattinson: Optional[int] = None
    star_Rupert_Grint: Optional[int] = None
    star_Ryan_Reynolds: Optional[int] = None
    star_Steve_Carell: Optional[int] = None
    star_Tom_Cruise: Optional[int] = None
    star_Tom_Hanks: Optional[int] = None
    star_Vin_Diesel: Optional[int] = None
    star_Vincent_Cassel: Optional[int] = None
    star_Will_Smith: Optional[int] = None
    star_Zoe_Saldana: Optional[int] = None
    prod_Anthony_Russo: Optional[int] = None
    prod_Chris_Morgan: Optional[int] = None
    prod_Christopher_Markus: Optional[int] = None
    prod_Christopher_Nolan: Optional[int] = None
    prod_Clint_Eastwood: Optional[int] = None
    prod_Dany_Boon: Optional[int] = None
    prod_David_Koepp: Optional[int] = None
    prod_David_Yates: Optional[int] = None
    prod_Fabien_Onteniente: Optional[int] = None
    prod_Franck_Dubosc: Optional[int] = None
    prod_Gore_Verbinski: Optional[int] = None
    prod_Guillaume_Canet: Optional[int] = None
    prod_JJ_Abrams: Optional[int] = None
    prod_Jeff_Nathanson: Optional[int] = None
    prod_Joe_Russo: Optional[int] = None
    prod_Jon_Favreau: Optional[int] = None
    prod_Jonathan_Aibel: Optional[int] = None
    prod_Luc_Besson: Optional[int] = None
    prod_Melissa_Rosenberg: Optional[int] = None
    prod_Neal_Purvis: Optional[int] = None
    prod_Olivier_Baroux: Optional[int] = None
    prod_Peter_Jackson: Optional[int] = None
    prod_Philippa_Boyens: Optional[int] = None
    prod_Philippe_de_Chauveron: Optional[int] = None
    prod_Rick_Jaffa: Optional[int] = None
    prod_Ridley_Scott: Optional[int] = None
    prod_Sam_Raimi: Optional[int] = None
    prod_Simon_Kinberg: Optional[int] = None
    prod_Stephen_McFeely: Optional[int] = None
    prod_Steve_Kloves: Optional[int] = None
    prod_Steven_Spielberg: Optional[int] = None
    prod_Ted_Elliott: Optional[int] = None
    prod_Terry_Rossio: Optional[int] = None
    prod_Tim_Burton: Optional[int] = None

# nat_Grande-Bretagne: Optional[int] = None
# nat_Nouvelle-Zélande: Optional[int] = None
# nat_U.S.A.: Optional[int] = None
# star_Jean-Paul_Rouve: Optional[int] = None
# star_Robert_Downey_Jr.: Optional[int] = None

class MoviePrediction(BaseModel):
    film_title: str
    predicted_fr_entries: int
    # features: Dict[str, Any] = None

class BatchMovieInput(BaseModel):
    movies: List[MovieInput]


class BatchMoviePrediction(BaseModel):
    predictions: List[MoviePrediction]