# feature_engineering.py
import pandas as pd
import numpy as np
from datetime import datetime
import re
import ast
import calendar
from textblob import TextBlob
import logging
import re
import ast 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Définissez toutes les fonctions d'abord, puis la fonction principale

def transform_duration_to_minutes(df):
    def duration_to_minutes(duration_str):
        if pd.isna(duration_str):
            return 105  # Valeur par défaut
        
        # Si c'est déjà un nombre
        if isinstance(duration_str, (int, float)):
            return float(duration_str)
        
        # Convertir en string si ce n'est pas le cas
        duration_str = str(duration_str)
        
        # Extraire les heures (pattern "Xh" ou "X h")
        hours_match = re.search(r'(\d+)\s*h', duration_str)
        hours = int(hours_match.group(1)) if hours_match else 0
        
        # Extraire les minutes (pattern "Ymin" ou "Y min")
        minutes_match = re.search(r'(\d+)\s*min', duration_str)
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        
        # Si ni heures ni minutes trouvées, essayer de trouver juste un nombre
        if hours == 0 and minutes == 0:
            number_match = re.search(r'(\d+)', duration_str)
            if number_match:
                minutes = int(number_match.group(1))
        
        # Calculer la durée totale en minutes
        total_minutes = hours * 60 + minutes
        
        # Retourner une valeur par défaut si aucune durée trouvée
        return total_minutes if total_minutes > 0 else 105
    
    # Appliquer la fonction et convertir en Int64 (permet les valeurs nulles)
    df['duration'] = df['duration'].apply(duration_to_minutes).astype('Int64')
    return df

def add_synopsis_length(df):
    df['synopsis_length'] = df['synopsis'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
    return df

def extract_award_and_nomination_counts(df):
    def clean_awards(text):
        awards = 0
        nominations = 0
        if pd.isna(text) or str(text).strip() == "":
            return awards, nominations
        match_awards = re.search(r'(\d+)\sprix', str(text), re.IGNORECASE)
        match_nominations = re.search(r'(\d+)\snomination', str(text), re.IGNORECASE)
        if match_awards:
            awards = int(match_awards[1])
        if match_nominations:
            nominations = int(match_nominations[1])
        return awards, nominations

    awards_data = df['awards'].apply(clean_awards)
    df['award_count'] = awards_data.apply(lambda x: int(x[0]) if pd.notna(x[0]) else 0)
    df['nomination_count'] = awards_data.apply(lambda x: int(x[1]) if pd.notna(x[1]) else 0)
    df['award_binary'] = df['award_count'].apply(lambda x: 1 if x != 0 else 0)
    df['nomination_binary'] = df['nomination_count'].apply(lambda x: 1 if x != 0 else 0)
    return df

def clean_trailer_views_column(df, column_name='trailer_views'):
    def extract_trailer_views_count(text):
        if pd.isna(text):
            return 0  # Valeur par défaut au lieu de pd.NA
        cleaned = re.sub(r"[^\d]", "", str(text))
        return int(cleaned) if cleaned else 0  # Valeur par défaut au lieu de pd.NA

    df[f"{column_name}_num"] = df[column_name].apply(extract_trailer_views_count)
    return df

def add_filming_secrets_num(df):
    def extract_number(text):
        if pd.isna(text):
            return 0  # Valeur par défaut
        cleaned = str(text).replace(" ", "")
        try:
            return int(cleaned)
        except ValueError:
            match = re.search(r'(\d+)', cleaned)
            return int(match[1]) if match else 0  # Valeur par défaut

    df['filming_secrets_num'] = df['filming_secrets'].apply(lambda x: extract_number(x))
    
    return df

def assign_top_distributor_score(df):
    top_distributor = {
        'walt disney': 3.0,
        'marvel studios': 3.0,
        'universal': 2.5,
        'paramount': 2.5,
        'warner bros': 2.5,
        'sony': 2.0,
        'columbia': 2.0,
        '20th century': 2.0,
        'studiocanal': 2.0,
        'gaumont': 2.0,
        'pathé': 2.0,
        'netflix': 2.0,
        'snd': 1.8,
        'diaphana': 1.8,
        'memento': 1.5,
        'apollo': 1.5,
        'ufo': 1.2,
        'tf1': 1.2,
        'metropolitan': 1.2,
        'pyramide': 1.2,
        'losange': 1.2,
        'le pacte': 1.0,
        'wild bunch': 1.0,
        'kmbo': 1.0,
        'jhr': 1.0,
        'gebeka': 1.0,
        'rezo': 1.0
    }

    df['top_distributor_score'] = df['distributor'].apply(
        lambda x: 1 if isinstance(x, str) and any(distributor.lower() in str(x).lower() for distributor in top_distributor) else 0.5
    )
    return df

def compute_distributor_power(df):
    # Weight dictionaries (normalized)
    studio_weights = {
        'walt disney': 3.0,
        'marvel studios': 3.0,
        'universal': 2.5,
        'paramount': 2.5,
        'warner bros': 2.5,
        'sony': 2.0,
        'columbia': 2.0,
        '20th century': 2.0,
        'netflix': 2.0,
    }

    distributor_weights = {
        'walt disney': 3.0,
        'universal': 2.5,
        'paramount': 2.5,
        'warner bros': 2.5,
        'sony': 2.0,
        'studiocanal': 2.0,
        'gaumont': 2.0,
        'pathÃ©': 2.0,
        'netflix': 2.0,
        'snd': 1.8,
        'diaphana': 1.8,
        'memento': 1.5,
        'apollo': 1.5,
        'ufo': 1.2,
        'tf1': 1.2,
        'metropolitan': 1.2,
        'pyramide': 1.2,
        'losange': 1.2,
    }

    independent_weights = {
        'le pacte': 1.0,
        'wild bunch': 1.0,
        'kmbo': 1.0,
        'jhr': 1.0,
        'gebeka': 1.0,
        'rezo': 1.0,
    }

    # Normalize keys
    studio_weights = {k.lower(): v for k, v in studio_weights.items()}
    distributor_weights = {k.lower(): v for k, v in distributor_weights.items()}
    independent_weights = {k.lower(): v for k, v in independent_weights.items()}

    # Function to compute power from fuzzy matching
    def compute_power_fuzzy(distributor):
        if not isinstance(distributor, str):
            return 0  # Valeur par défaut
            
        name = distributor.lower().strip()

        # Independent check
        for key, weight in independent_weights.items():
            if key in name:
                return weight

        # Studio & distributor
        studio_score = next((v for k, v in studio_weights.items() if k in name), 0)
        dist_score = next((v for k, v in distributor_weights.items() if k in name), 0)

        if studio_score and dist_score:
            return studio_score + dist_score
        elif studio_score:
            return studio_score
        elif dist_score:
            return dist_score
        return 0

    # Apply to DataFrame
    df['distributor_power'] = df['distributor'].apply(compute_power_fuzzy)

    return df

def assign_franchise_level(df):
    # Full list of franchises relevant in the French market
    top_franchises = [
    'mad max', 'iron man', 'captain america', 'thor', 'wolverine',
    'mission impossible', 'terminator', 'hunger games', 'twilight',
    'pirates des caraïbes', 'le hobbit', 'matrix', 'minecraft',
    'les minions', 'john wick', 'alien', 'predator', 'rocky', 'rambo',
    'conjuring', 'saw', 'scream', 'halloween', 'barbie',
    'harry potter', 'star wars', 'spider-man', 'avengers', 'x-men',
    'batman', 'jurassic', 'fast and furious', 'transformers',
    'le seigneur des anneaux', 'shrek', 'le roi lion', 'indiana jones',
    'l\'âge de glace', 'deadpool', 'super mario bros', 'les animaux fantastiques',
    'avatar', 'les dents de la mer', 'les gardiens de la galaxie'
]
    
    # Level 4 — Mega franchises with global cultural dominance and massive French box office
    mega_franchises = [
        'avatar', 'jurassic', 'star wars', 'harry potter',
        'avengers', 'fast and furious', 'le roi lion', 'spider-man'
    ]

    # Level 3 — Strong global franchises with high awareness and frequent sequels
    major_franchises = [
        'iron man', 'captain america', 'x-men', 'batman',
        'transformers', 'deadpool', 'les minions', 'moi moche et méchant',
        'mission impossible', 'shrek', 'le seigneur des anneaux', 'l\'âge de glace',
        'super mario bros'
    ]

    # Level 2 — Known franchises with good brand recall and fan bases
    big_franchises = [
        'mad max', 'hunger games', 'twilight', 'john wick', 'thor', 'wolverine',
        'matrix', 'pirates des caraïbes', 'le hobbit', 'conjuring',
        'les animaux fantastiques', 'indiana jones', 'les gardiens de la galaxie',
        'minecraft', 'rocky', 'rambo', 'alien', 'predator',
        'scream', 'saw', 'halloween', 'barbie', 'terminator', 'les dents de la'
    ]

    # Detection function using franchise level
    def identify_franchise_level(title):
        if not isinstance(title, str):
            return 0

        title_lower = title.lower()

        if any(f in title_lower for f in mega_franchises):
            return 4
        if any(f in title_lower for f in major_franchises):
            return 3
        if any(f in title_lower for f in big_franchises):
            return 2
        return 1 if any(f in title_lower for f in top_franchises) else 0

    # Apply the function to the DataFrame
    df['franchise_level'] = df['film_title'].apply(identify_franchise_level)

    return df

def add_franchise_blockbuster_score(df):
    # 1. Base score from franchise level
    base_score = df['franchise_level'] * 2

    # 2. Bonus for each franchise category
    bonus_cols = [
        'is_superhero_franchise',
        'is_animation_franchise',
        'is_action_franchise',
        'is_gaming_franchise',
    ]
    
    # Make sure all bonus columns exist
    for col in bonus_cols:
        if col not in df.columns:
            df[col] = 0
            
    bonus_score = df[bonus_cols].sum(axis=1)

    # 3. Bonus for strong distributors
    strong_distributors = [
        'warner', 'disney', 'universal', 'paramount', 
        'sony', '20th century', 'pathé', 'gaumont', 'netflix'
    ]
    pattern = '|'.join([sd.replace('.', r'.') for sd in strong_distributors])
    dist_bonus = df['distributor'].fillna('').str.lower().str.contains(pattern, regex=True).astype(int)

    # 4. Final score
    df['franchise_blockbuster_score'] = base_score + bonus_score + dist_bonus
    return df

def create_licence_features(df):
    superhero_franchises = [
        'marvel', 'avengers', 'captain america', 'iron man', 'thor', 'hulk',
        'batman', 'superman', 'dc', 'justice league', 'x-men', 'spider-man',
        'wolverine', 'deadpool', 'les gardiens de la galaxie'
]
    
    animation_franchises = [
        'disney', 'pixar', 'dreamworks', 'illumination', 'vaiana', 'astérix',
        'shrek', 'toy story', 'madagascar', 'minions', 'vice-versa',
        'moi, moche et méchant', 'l\'âge de glace', 'le roi lion', 'super mario bros'
    ]

    action_franchises = [
        'mad max', 'fast and furious', '007', 'mission : impossible',
        'star wars', 'harry potter', 'hunger games', 'jurassic', 'terminator',
        'dune', 'john wick', 'matrix', 'indiana jones', 'le seigneur des anneaux',
        'le hobbit', 'barbie', 'conjuring', 'saw', 'scream', 'halloween',
        'rocky', 'rambo', 'alien', 'predator', 'les animaux fantastiques',
        'les dents de la'
    ]
    
    gaming_franchises = [
        'minecraft', 'mario', 'super mario bros', 'pokemon', 'tomb raider',
        'assassin\'s creed', 'sonic', 'mortal kombat', 'uncharted', 'warcraft'
    ]

    # ----- Column generation -----
    def contains_any(text, keywords):
        return any(f in text for f in keywords)
        
    # Normalize column
    df['film_title_clean'] = df['film_title'].astype(str).str.lower()

    df['is_superhero_franchise'] = df['film_title_clean'].apply(
        lambda x: int(contains_any(x, superhero_franchises))
    )

    df['is_animation_franchise'] = df['film_title_clean'].apply(
        lambda x: int(contains_any(x, animation_franchises))
    )

    df['is_action_franchise'] = df['film_title_clean'].apply(
        lambda x: int(contains_any(x, action_franchises))
    )

    df['is_gaming_franchise'] = df['film_title_clean'].apply(
        lambda x: int(contains_any(x, gaming_franchises))
    )

    # Any type of known licence
    df['is_licence'] = (df['is_superhero_franchise'] |
                        df['is_animation_franchise'] |
                        df['is_action_franchise'] |
                        df['is_gaming_franchise'])

    # ----- Sequel Detection -----
    sequel_indicators = ['2', '3', '4', '5', 'ii', 'iii', 'iv', 'v', 'vi', 'le retour', 'la suite',
                        'chapitre', 'épisode', 'saga', 'partie', 'part', 'volume']

    df['is_sequel'] = df['film_title_clean'].apply(
        lambda x: int(contains_any(x, sequel_indicators))
    )

    # Drop helper column
    df.drop(columns=['film_title_clean'], inplace=True)

    return df

def calculate_synopsis_sentiment(df):
    df['synopsis_sentiment'] = df['synopsis'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    return df

def categorize_synopsis(df):
    def categorize_synopsis_length(num):
        if num != np.nan:
            if num <= 200:
                return "not long"
            elif 200 < num < 700:
                return "normal"
            elif 700 < num < 1000:
                return "long"
        else:
            return "very long"

    def categorize_synopsis_sentiment(num):
        if num != np.nan:
            if num <= -0.2:
                return "negative"
            elif -0.2 < num < 0.2:
                return "neutral"
            elif 0.2 < num < 0.5:
                return "positive"
        else:
            return "very positive"

    df['synopsis_length_categorized'] = df['synopsis_length'].apply(lambda x: categorize_synopsis_length(x))
    df['synopisis_sentiment_categorized'] = df['synopsis_sentiment'].apply(lambda x: categorize_synopsis_sentiment(x))

    return df

def categorize_duration(df):
    def categorize_duration_single(duration):
        if pd.isna(duration) or duration < 70:
            return "short-film"
        elif 70 < duration < 160:
            return "normal-film"
        elif 160 < duration < 210:
            return "long-film"
        else:
            return "very long film"

    df['duration_classified'] = df['duration'].apply(lambda x: categorize_duration_single(x))
    df['duration_binary'] = df['duration'].apply(lambda x: 1 if pd.notna(x) and x > 120 else 0)

    return df

def add_broadcast_category(df):
    if 'broadcast_category' not in df.columns:
        df['broadcast_category'] = 'en salle'  # Valeur par défaut
    df['broadcast_category'] = df['broadcast_category'].astype('category')
    return df

def add_trailer_views_binary(df):
    def to_binary(text):
        if pd.isna(text):
            return 0
        cleaned = re.sub(r"[^\d]", "", str(text))
        return 1 if cleaned and int(cleaned) > 0 else 0

    df['trailer_views_num_binary'] = df['trailer_views'].apply(to_binary).astype('category')
    return df

def categorize_mcu(df):
    mcu_titles = [
        'avengers', 'iron man', 'captain america', 'thor', 'hulk',
        'black panther', 'doctor strange', 'les gardiens de la galaxie',
        'ant-man', 'spider-man', 'les eternels', 'shang-chi', 'black widow',
        'marvels', 'wanda', 'vision', 'falcon', 'le soldat de l\'hiver'
    ]

    df['is_mcu'] = df['film_title'].apply(
        lambda x: 1 if isinstance(x, str) and any(title in x.lower() for title in mcu_titles) else 0
    )

    return df

def categorize_likely_blockbusters(df):
    likely_blockbusters = [
        'avengers', 'star wars', 'jurassic world', 'avatar',
        'harry potter', 'spider-man', 'batman', 'superman',
        'fast and furious', 'frozen', 'la reine des neiges',
        'minions', 'le roi lion',
        'the dark knight', 'barbie', 'oppenheimer',
        'mario', 'les animaux fantastiques'
    ]

    df['is_likely_blockbuster'] = df['film_title'].apply(
        lambda x: 1 if isinstance(x, str) and any(f.lower() in x.lower() for f in likely_blockbusters) else 0
    )

    return df

def create_major_studio_feature(df):
    major_studios = [
        'disney', 'warner', 'universal', 'sony', 'paramount',
        '20th century', 'fox', 'gaumont', 'pathé',
        'netflix', 'amazon', 'apple'
    ]

    df['is_major_studio'] = df['distributor'].apply(
        lambda x: 1 if isinstance(x, str) and any(studio.lower() in x.lower() for studio in major_studios) else 0
    )

    return df

def create_french_major_studio_feature(df):
    french_majors = [
        'studiocanal', 'gaumont', 'pathé', 'ufp', 'snd', 'diaphana'
    ]
    df['is_french_major_studio'] = df['distributor'].apply(
        lambda x: 1 if isinstance(x, str) and any(fm.lower() in x.lower() for fm in french_majors) else 0
    )

    return df

def create_composite_features(df):
    # Make sure is_licence exists
    if 'is_licence' not in df.columns:
        df['is_licence'] = 0
    
    df['major_studio_and_licence'] = (
        df['is_major_studio'] & df['is_licence']
    ).astype(int)
        
    df['french_major_and_licence'] = (
        df['is_french_major_studio'] & df['is_licence']
    ).astype(int)

    return df

def create_interaction_features(df):
    """
    Creates advanced interaction and multiplier features that capture:
    - Franchise and major studio combinations
    - Estimated marketing power
    - Connected universe detection (e.g., superhero sagas)
    - Success amplification scores based on known blockbusters, MCU, franchise levels, and prestige.
    """

    # Interaction between major studios and franchises
    df['major_studio_x_franchise'] = df['is_major_studio'] * df['franchise_level']
    
    # Connected universe flag, e.g., Marvel/DC films with multiple levels
    df['is_connected_universe'] = (
        (df['is_superhero_franchise'] == 1) & 
        (df['franchise_level'] >= 2)
    ).astype(int)

    # Estimated marketing potential from studio and franchise weight
    df['estimated_marketing_power'] = (
        df['franchise_level'] * 2 + df['is_major_studio'] * 1.5
    )

    # Success amplifier using vectorized operations instead of apply
    conditions = [
        (df['is_likely_blockbuster'] == 1),
        (df['is_mcu'] == 1) & df['film_title'].str.contains('avengers', case=False, na=False),
        (df['is_mcu'] == 1),
        (df['franchise_level'] == 4),
        (df['franchise_level'] == 3),
        (df['franchise_level'] == 2)
    ]
    values = [3.0, 2.2, 1.8, 1.7, 1.5, 1.2]

    df['success_amplifier'] = np.select(conditions, values, default=1.0)
    
    return df

def add_year_of_production(df):
    if 'year_of_production' not in df.columns:
        # Essayer d'extraire l'année de release_date
        if 'release_date' in df.columns:
            df['year_of_production'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year.astype(str)
        else:
            df['year_of_production'] = '2023'  # Valeur par défaut
    
    df['year_of_production'] = df['year_of_production'].astype('category')
    
    return df

def process_french_dates(df, date_column='release_date_france'):
    # S'assurer que la colonne existe
    if date_column not in df.columns:
        logger.warning(f"Column {date_column} not found in DataFrame. Using release_date instead.")
        if 'release_date' in df.columns:
            # Convertir release_date en release_date_france
            df[date_column] = df['release_date']
        else:
            logger.warning("release_date also not found. Using current date.")
            df[date_column] = pd.Timestamp.now().strftime('%Y-%m-%d')
    
    # Convertir en datetime
    df['release_date_france_datetime'] = pd.to_datetime(df[date_column], errors='coerce')
    
    # Extraire les composantes
    df['release_date_france_year'] = df['release_date_france_datetime'].dt.year
    df['release_date_france_month_num'] = df['release_date_france_datetime'].dt.month
    df['release_date_france_day'] = df['release_date_france_datetime'].dt.day
    
    # Convertir les mois numériques en noms
    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April', 
        5: 'May', 6: 'June', 7: 'July', 8: 'August', 
        9: 'September', 10: 'October', 11: 'November', 12: 'December'
    }
    
    df['release_date_france_month'] = df['release_date_france_month_num'].map(
        lambda x: month_names.get(x) if pd.notna(x) else None
    )
    
    return df

def add_season_column(df):
    def get_season(month):
        if pd.isna(month):
            return "Spring"  # Valeur par défaut
        
        month = int(month) if isinstance(month, (int, float)) else month
        
        # Northern hemisphere seasons
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Autumn"
    
    # Utiliser release_date_france_month_num si disponible, sinon extraire depuis release_date
    if 'release_date_france_month_num' in df.columns:
        df['release_season'] = df['release_date_france_month_num'].apply(get_season)
    else:
        # Essayer d'extraire le mois à partir de release_date
        if 'release_date' in df.columns:
            df['release_season'] = pd.to_datetime(df['release_date'], errors='coerce').dt.month.apply(get_season)
        else:
            df['release_season'] = "Spring"  # Valeur par défaut
    
    return df

def clean_film_title(df):
    df['film_title'] = df['film_title'].astype(str).str.strip()
    df['film_title_length'] = df['film_title'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
    return df

def add_director(df):
    if 'director' in df.columns:
        df['director'] = df['director'].astype(str)
    else:
        df['director'] = ""  # Valeur par défaut
    return df

def add_synopsis_binary(df):
    df['synopsis_binary'] = df['synopsis_length'].apply(lambda x: 1 if pd.notnull(x) and x > 0 else 0)
    return df

def add_director_binary(df):
    df['director_binary'] = df['director'].apply(lambda x: 1 if pd.notnull(x) and x != "" and x != "nan" else 0)
    return df

def process_list_columns(df):
    def split_list(text, separator=','):
        if pd.isna(text) or str(text).strip() == "" or str(text) == "nan":
            return []
        return [x.strip() for x in str(text).split(separator) if x.strip()]

    # Process producers column
    if 'producers' in df.columns:
        df['producers_list'] = df['producers'].apply(lambda x: split_list(x))
    else:
        df['producers_list'] = [[]]
    df['producers_count'] = df['producers_list'].apply(len)
    df['producers_count_binary'] = df['producers_count'].apply(lambda x: 1 if x > 0 else 0)

    # Process top_stars column
    if 'top_stars' in df.columns:
        df['top_stars_list'] = df['top_stars'].apply(lambda x: split_list(x))
    else:
        df['top_stars_list'] = [[]]
    df['top_stars_count'] = df['top_stars_list'].apply(len)
    df['top_stars_count_binary'] = df['top_stars_count'].apply(lambda x: 1 if x > 0 else 0)

    # Process languages column
    if 'languages' in df.columns:
        df['languages_list'] = df['languages'].apply(lambda x: split_list(x))
    else:
        df['languages_list'] = [[]]
    df['languages_count'] = df['languages_list'].apply(len)

    # Process nationality column
    if 'film_nationality' in df.columns:
        df['nationality_list'] = df['film_nationality'].apply(lambda x: split_list(x))
    else:
        df['nationality_list'] = [[]]
    df['nationality_list_count'] = df['nationality_list'].apply(len)
    df['nationality_list_binary'] = df['nationality_list_count'].apply(lambda x: 1 if x > 0 else 0)

    # Process associated_genres column
    if 'associated_genres' in df.columns:
        df['associated_genres_list'] = df['associated_genres'].apply(lambda x: split_list(x))
    else:
        # Utiliser une colonne alternative si elle existe ou créer une vide
        df['associated_genres_list'] = [[]]
    df['associated_genres_count'] = df['associated_genres_list'].apply(len)

    return df

def add_distributor_binary(df):
    df['distributor_binary'] = df['distributor'].apply(lambda x: 1 if pd.notnull(x) and str(x) != "" and str(x) != "nan" else 0)
    return df

def add_press_rating_binary(df):
    # Create binary column (1 if press rating exists, 0 otherwise)
    df['press_rating_binary'] = df['press_rating'].apply(lambda x: 1 if pd.notna(x) else 0)
    return df

def add_viewer_rating_binary(df):
    # Create binary column (1 if viewer rating exists, 0 otherwise)
    df['viewer_rating_binary'] = df['viewer_rating'].apply(lambda x: 1 if pd.notna(x) else 0)
    return df

def clean_director_column(df):
    # Strip whitespace and fill NA values with "unknown"
    df['director'] = df['director'].str.strip()
    df['director'] = df['director'].fillna("unknown")
    return df

def parse_stringified_lists(df, columns=['top_stars_list', 'languages_list', 'nationality_list', 'producers_list']):
    """Convert stringified lists to actual Python lists"""
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)
    return df

# #######

# def create_star_features(df):
#     """Create binary features for each top star"""
#     if 'top_stars_list' not in df.columns:
#         return df
        
#     # List of stars from your data (can be expanded)
#     stars = [
#         'André Dussollier', 'Benoît Poelvoorde', 'Brad Pitt', 'Chris Evans',
#         'Chris Pratt', 'Christian Clavier', 'Clovis Cornillac', 'Daniel Craig',
#         'Daniel Radcliffe', 'Dany Boon', 'Dwayne Johnson', 'Emma Watson',
#         'Ewan McGregor', 'Franck Dubosc', 'Gad Elmaleh', 'George Clooney',
#         'Gilles Lellouche', 'Guillaume Canet', 'Gérard Depardieu', 'Gérard Lanvin',
#         'Hugh Jackman', 'Isabelle Nanty', 'Jamel Debbouze', 'Jason Statham',
#         'Jean Dujardin', 'Jean Reno', 'Jean-Paul Rouve', 'Johnny Depp',
#         'José Garcia', 'Kad Merad', 'Keira Knightley', 'Kristen Stewart',
#         'Leonardo DiCaprio', 'Marion Cotillard', 'Mark Ruffalo', 'Matt Damon',
#         'Robert Downey Jr.', 'Robert Pattinson', 'Rupert Grint', 'Ryan Reynolds',
#         'Steve Carell', 'Tom Cruise', 'Tom Hanks', 'Vin Diesel',
#         'Vincent Cassel', 'Will Smith', 'Zoe Saldana'
#     ]
    
#     # Create features
#     for star in stars:
#         star_col = f'star_{star}'
#         df[star_col] = df['top_stars_list'].apply(
#             lambda x: 1 if isinstance(x, list) and star in x else 0
#         )
    
#     return df

# def create_nationality_features(df):
#     """Create binary features for each nationality"""
#     if 'nationality_list' not in df.columns:
#         return df
        
#     # List of nationalities from your data
#     nationalities = [
#         'Allemagne', 'Australie', 'Belgique', 'Canada', 'Espagne', 
#         'France', 'Grande-Bretagne', 'Italie', 'Japon', 
#         'Nouvelle-Zélande', 'U.S.A.'
#     ]
    
#     # Create features
#     for nat in nationalities:
#         nat_col = f'nat_{nat}'
#         df[nat_col] = df['nationality_list'].apply(
#             lambda x: 1 if isinstance(x, list) and nat in x else 0
#         )
    
#     return df

# def create_language_features(df):
#     """Create binary features for each language"""
#     if 'languages_list' not in df.columns:
#         return df
        
#     # List of languages from your data
#     languages = [
#         'ARABIC', 'Allemand', 'Anglais', 'Chinois', 'Espagnol', 
#         'Français', 'Hébreu', 'Italien', 'Japonais', 'Latin',
#         'Mandarin', 'Portugais', 'Russe'
#     ]
    
#     # Create features
#     for lang in languages:
#         lang_col = f'lang_{lang}'
#         df[lang_col] = df['languages_list'].apply(
#             lambda x: 1 if isinstance(x, list) and lang in x else 0
#         )
    
#     return df

# def create_producer_features(df):
#     """Create binary features for each producer"""
#     if 'producers_list' not in df.columns:
#         return df
        
#     # List of producers from your data
#     producers = [
#         'Anthony Russo', 'Chris Morgan', 'Christopher Markus', 'Christopher Nolan',
#         'Clint Eastwood', 'Dany Boon', 'David Koepp', 'David Yates',
#         'Fabien Onteniente', 'Franck Dubosc', 'Gore Verbinski', 'Guillaume Canet',
#         'J.J. Abrams', 'Jeff Nathanson', 'Joe Russo', 'Jon Favreau',
#         'Jonathan Aibel', 'Luc Besson', 'Melissa Rosenberg', 'Neal Purvis',
#         'Olivier Baroux', 'Peter Jackson', 'Philippa Boyens', 'Philippe de Chauveron',
#         'Rick Jaffa', 'Ridley Scott', 'Sam Raimi', 'Simon Kinberg',
#         'Stephen McFeely', 'Steve Kloves', 'Steven Spielberg', 'Ted Elliott',
#         'Terry Rossio', 'Tim Burton'
#     ]
    
#     # Create features
#     for prod in producers:
#         prod_col = f'prod_{prod}'
#         df[prod_col] = df['producers_list'].apply(
#             lambda x: 1 if isinstance(x, list) and prod in x else 0
#         )
    
#     return df




def preprocess_movie_data(movie_data):
    """
    Process raw movie data and transform it into the format required by the model
    
    Args:
        movie_data: DataFrame or dict containing raw movie data
    
    Returns:
        DataFrame with processed features
    """
    # If input is a csv, convert to DataFrame
    if isinstance(movie_data, str) and movie_data.endswith("csv"):
        df = pd.DataFrame([movie_data])
    else:
        df = pd.DataFrame(movie_data)
    
    if isinstance(movie_data, list):
        df = pd.DataFrame(movie_data)
    
    required_columns = [
        'film_title','film_url','film_image_url', 'release_date', 'duration', 'age_classification','producers','director', 'top_stars','press_rating','viewer_rating',
        'languages','distributor','year_of_production','film_nationality','filming_secrets','fr_entry_week','us_entry_week','fr_entries','us_entries','awards','budget',
        'associated_genres','press_critics_count','viewer_critics_count','broadcast_category','trailer_views','synopsis'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    
    # Initialisations importantes 
    df['franchise_level'] = 0  
    df['is_superhero_franchise'] = 0
    df['is_animation_franchise'] = 0
    df['is_action_franchise'] = 0
    df['is_gaming_franchise'] = 0
    df['is_licence'] = 0
    df['is_major_studio'] = 0
    df['is_french_major_studio'] = 0
    df['release_date_france_year'] = None
    df['release_date_france_month'] = None
    df['release_date_france_day'] = None
    df['release_season'] = None
    df['press_rating_binary'] = 0
    df['viewer_rating_binary'] = 0
    df['nationality_list_binary'] = 0
    
    # Transformations
    df = transform_duration_to_minutes(df)
    df = add_synopsis_length(df)
    df = extract_award_and_nomination_counts(df)
    df = clean_trailer_views_column(df)
    df = add_filming_secrets_num(df)
    df = assign_top_distributor_score(df)
    df = compute_distributor_power(df)
    df = assign_franchise_level(df)  
    df = create_licence_features(df)
    df = calculate_synopsis_sentiment(df)
    df = categorize_synopsis(df)
    df = categorize_duration(df)
    df = add_broadcast_category(df)
    df = add_trailer_views_binary(df)
    df = categorize_mcu(df)
    df = categorize_likely_blockbusters(df)
    df = create_major_studio_feature(df)
    df = create_french_major_studio_feature(df)
    df = create_composite_features(df)
    df = clean_director_column(df)
    df = parse_stringified_lists(df)
    
    df = add_franchise_blockbuster_score(df)

    df = create_interaction_features(df)
    df = add_year_of_production(df)
    # df = create_star_features(df)
    # df = create_nationality_features(df)
    # df = create_language_features(df)
    # df = create_producer_features(df)
    
    if 'release_date' in df.columns:
        # Créer une copie pour process_french_dates
        df['release_date_france'] = df['release_date']
        df = process_french_dates(df)
        
    df = add_season_column(df)
    df = clean_film_title(df)
    df = add_director(df)
    df = add_synopsis_binary(df)
    df = add_director_binary(df)
    df = process_list_columns(df)
    df = add_distributor_binary(df)
    df = add_press_rating_binary(df)
    df = add_viewer_rating_binary(df)
    
    return df