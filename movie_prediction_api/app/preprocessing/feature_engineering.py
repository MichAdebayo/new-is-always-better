import pandas as pd
import numpy as np
from datetime import datetime
import re
import ast
import calendar
from textblob import TextBlob
import logging
import re 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    
    # Transformations
    df=transform_duration_to_minutes(df)
    df=add_synopsis_length(df)
    df=extract_award_and_nomination_counts(df)
    df=clean_trailer_views_column(df)
    df=add_filming_secrets_num(df)
    df=distributor_scoring(df)
    df=assign_top_distributor_score(df)
    df=compute_distributor_power(df)
    df=add_franchise_blockbuster_score(df)
    df=assign_franchise_level(df)
    df=create_licence_features(df)
    df=calculate_synopsis_sentiment(df)
    df=categorize_synopsis(df)
    df=categorize_duration(df)
    df=add_broadcast_category(df)
    df=add_trailer_views_binary(df)
    df=categorize_mcu(df)
    df=categorize_likely_blockbusters(df)
    df=create_major_studio_feature(df)
    df=create_french_major_studio_feature(df)
    df=create_composite_features(df)
    df=create_interaction_features(df)
    df=add_year_of_production(df)
    df=process_french_dates(df)
    df=add_season_column(df)
    df=clean_film_title(df)
    df=add_director(df)
    df=add_synopsis_binary(df)
    df=add_director_binary(df)
    df=process_list_columns(df)
    df=add_distributor_binary(df)
    return df


def transform_duration_to_minutes(df):
    def duration_to_minutes(duration_str):
        if pd.isna(duration_str):
            return None
        if not isinstance(duration_str, str):
            return duration_str  # Already processed or invalid
        if match := re.search(r'(\d+)\sh\s(\d+)?', duration_str):
            hours = int(match[1])
            minutes = int(match[2]) if match[2] else 0
            return hours * 60 + minutes
        return None

    df['duration'] = df['duration'].apply(duration_to_minutes).astype('Int64')
    return df

def add_synopsis_length(df):
    df['synopsis_length'] = df['synopsis'].apply(lambda x: len(x) if pd.notna(x) else 0)
    return df

def extract_award_and_nomination_counts(df):
    def clean_awards(text):
        awards = None
        nominations = None
        if pd.isna(text) or text.strip() == "":
            return awards, nominations
        match_awards = re.search(r'(\d+)\sprix', text, re.IGNORECASE)
        match_nominations = re.search(r'(\d+)\snomination', text, re.IGNORECASE)
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
            return pd.NA
        cleaned = re.sub(r"[^\d]", "", str(text))
        return int(cleaned) if cleaned else pd.NA

    df[f"{column_name}_num"] = df[column_name].apply(extract_trailer_views_count)
    return df

def add_filming_secrets_num(df):
    def extract_number(text):
        if pd.isna(text):
            return None
        cleaned = text.replace(" ", "")
        try:
            return int(cleaned)
        except ValueError:
            match = re.search(r'(\d+)', cleaned)
            return int(match[1]) if match else None

    df['filming_secrets_num'] = df['filming_secrets'].apply(lambda x: extract_number(x))
    df['filming_secrets_num'] = df['filming_secrets_num'].apply(lambda x: int(x) if pd.notna(x) else 0)

    return df

def distributor_scoring(df):
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
        lambda x: top_distributor.get(x.lower(), 0.5) if isinstance(x, str) else 0.5
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
        'avatar', 'les dents de la', 'les gardiens de la galaxie'
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

    # Check consistency: all franchises must be included in a level
    unassigned = set(top_franchises) - set(mega_franchises) - set(major_franchises) - set(big_franchises)
    assert len(unassigned) == 0, f"Missing franchises in level assignments: {unassigned}"

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
    df['synopsis_sentiment_categorized'] = df['synopsis_sentiment'].apply(lambda x: categorize_synopsis_sentiment(x))

    return df

def categorize_duration(df):
    def categorize_duration_single(duration):
        if duration < 70:
            return "short-film"
        elif 70 < duration < 160:
            return "normal-film"
        elif 160 < duration < 210:
            return "long-film"
        else:
            return "very long film"

    df['duration_classified'] = df['duration'].apply(lambda x: categorize_duration_single(x))

    return df

def add_broadcast_category(df):
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

    df['is_major_studio'] = df.get('distributor', '').str.lower().apply(lambda x: 1 if any(studio in x for studio in major_studios) else 0)

    return df

def create_french_major_studio_feature(df):

    french_majors = [
        'studiocanal', 'gaumont', 'pathé', 'ufp', 'snd', 'diaphana'
    ]
    df['is_french_major_studio'] = df.get('distributor', '').str.lower().apply(lambda x: 1 if any(fm in x for fm in french_majors) else 0)

    return df

def create_composite_features(df):
  
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

    Assumes the following columns already exist:
    - 'franchise_level', 'is_major_studio', 'is_superhero_franchise',
    'is_mega_blockbuster', 'is_mcu', 'film_title',
    'has_prestige_director', 'has_famous_actor'
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
    if 'year_of_production' in df.columns:
        df['year_of_production'] = df['year_of_production'].astype('category')
    else:
        print("Warning: 'year_of_production' column not found in DataFrame.")
    
    return df

def process_french_dates(df, date_column='release_date_france'):
    # Mapping for French month names to numbers
    month_mapping = {
        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
    }
    
    def parse_release_date(date_str):
        # Return None if the input is missing (NaN)
        if pd.isna(date_str):
            return None
            
        # Split the input string into parts (words)
        parts = date_str.strip().split()
        
        # If the format is "day month year" (3 parts)
        if len(parts) == 3:
            day, month_fr, year = parts
            
            # Convert French month to numeric format
            month = month_mapping.get(month_fr.lower())
            
            # Return None if the month is not valid
            if not month:
                return None
                
            try:
                # Build a datetime object and return the date as "DD-MM-YYYY"
                date_obj = datetime.strptime(f"{day.zfill(2)}-{month}-{year}", "%d-%m-%Y")
                return date_obj.strftime("%d-%m-%Y")
            except ValueError:
                # Handle invalid day/month/year combinations (e.g., "31 février")
                return None
                
        # If the format is "month year" (2 parts)
        elif len(parts) == 2:
            month_fr, year = parts
            
            # Convert French month to numeric format
            month = month_mapping.get(month_fr.lower())
            
            # Return formatted string or None if the month is invalid
            if not month:
                return None
            return f"{month}-{year}"
            
        # If the format is not recognized, return None
        else:
            return None
    
    # Step 1: Parse the French date strings
    df[f'{date_column}_parsed'] = df[date_column].apply(parse_release_date)
    
    # Step 2: Convert to datetime
    df[f'{date_column}_datetime'] = pd.to_datetime(df[f'{date_column}_parsed'], errors='coerce')
    
    # Step 3: Extract year, month, and day
    df[f'{date_column}_year'] = df[f'{date_column}_datetime'].dt.year
    df[f'{date_column}_month_num'] = df[f'{date_column}_datetime'].dt.month
    df[f'{date_column}_day'] = df[f'{date_column}_datetime'].dt.day
    
    # Step 4: Map month numbers to month names
    df[f'{date_column}_month'] = df[f'{date_column}_month_num'].map(
        lambda x: calendar.month_name[x] if pd.notnull(x) else np.nan)
    
    return df

def add_season_column(df, date_column='release_date_france', output_column='release_season'):
    def get_season(date_str):
        # Return None if input is missing
        if pd.isna(date_str):
            return None
        try:
            dt = datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            return None

        month = dt.month
        # Northern hemisphere seasons
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Autumn"
        
    df[output_column] = df[date_column].apply(get_season)

    return df   

def clean_film_title(df):
    df['film_title'] = df['film_title'].astype(str).str.strip()

    return df

def add_director(df):
    if 'director' in df.columns:
        df['director'] = df['director'].astype(str)
    else:
        print("Warning: 'director' column not found in DataFrame.")
    return df

def add_synopsis_binary(df):
    
    df['synopsis_binary'] = df['synopsis_length'].apply(lambda x: 1 if pd.notnull(x) and x != 0 else 0)

    return df

def add_director_binary(df):
   
    df['director_binary'] = df['director'].apply(lambda x: 1 if pd.notnull(x) and x != "" else 0)

    return df

def process_list_columns(df):
   
    def split_list(text, separator=','):
        if pd.isna(text) or text.strip() == "":
            return []
        return [x.strip() for x in text.split(separator) if x.strip()]

#Process producers column
    df['producers_list'] = df['producers'].apply(lambda x: split_list(x))
    df['producers_count'] = df['producers_list'].apply(len)
    df['producers_count_binary'] = df['producers_count'].apply(lambda x: 1 if x > 0 else 0)

#Process top_stars column
    df['top_stars_list'] = df['top_stars'].apply(lambda x: split_list(x))
    df['top_stars_count'] = df['top_stars_list'].apply(len)
    df['top_stars_count_binary'] = df['top_stars_count'].apply(lambda x: 1 if x > 0 else 0)

#Process languages column
    df['languages_list'] = df['languages'].apply(lambda x: split_list(x))
    df['languages_count'] = df['languages_list'].apply(len)

#Process nationality column
    df['nationality_list'] = df['nationality'].apply(lambda x: split_list(x))
    df['nationality_list_count'] = df['nationality_list'].apply(len)
    df['nationality_list_binary'] = df['nationality_list_count'].apply(lambda x: 1 if x > 0 else 0)

#Process associated_genres_allocine column
    df['associated_genres_allocine_list'] = df['associated_genres_allocine'].apply(lambda x: split_list(x))
    df['associated_genres_allocine_count'] = df['associated_genres_allocine_list'].apply(len)

    return df

def add_distributor_binary(df):
    
    df['distributor_binary'] = df['distributor'].apply(lambda x: 1 if pd.notnull(x) and x != "" else 0)

    return df




























def transform_basic_features(df):
    """
    Transform the basic features to expected format
    """
    # Create URL and image URL placeholders
    if 'film_url' not in df.columns:
        df['film_url'] = df['film_title'].apply(lambda x: f"https://www.allocine.fr/film/fichefilm_gen_cfilm={hash(x) % 1000000}.html")
    
    if 'film_image_url' not in df.columns:
        df['film_image_url'] = df['film_title'].apply(lambda x: f"https://fr.web.img3.acsta.net/c_310_420/img/default_movie_poster.jpg")
    
    # Create film_id if not exists
    if 'film_id' not in df.columns:
        df['film_id'] = df['film_title'].apply(lambda x: hash(x) % 1000000)
    
    # Convert duration from string to minutes
    if 'duration' in df.columns:
        df['duration'] = df['duration'].apply(parse_duration)
    
    # Parse year of production if it's a string
    if 'year_of_production' in df.columns and df['year_of_production'].dtype == 'object':
        df['year_of_production'] = df['year_of_production'].apply(lambda x: parse_year(x) if pd.notna(x) else None)
    
    # Ensure we have ratings (defaults)
    if 'press_rating' not in df.columns:
        df['press_rating'] = 2.5
    
    if 'viewer_rating' not in df.columns:
        df['viewer_rating'] = 3.0
    
    # Add default entries
    if 'fr_entries' not in df.columns:
        df['fr_entries'] = 0
    
    if 'us_entries' not in df.columns:
        df['us_entries'] = 0
    
    # Add budget placeholder
    if 'budget' not in df.columns:
        df['budget'] = '-'
    
    # Add ISO week placeholders
    if 'fr_entry_week_iso_week' not in df.columns:
        df['fr_entry_week_iso_week'] = df['release_date'].apply(lambda x: get_iso_week(x) if pd.notna(x) else None)
    
    if 'us_entry_week_iso_week' not in df.columns:
        df['us_entry_week_iso_week'] = df['release_date'].apply(lambda x: get_iso_week(x) if pd.notna(x) else None)
    
    # Add missing metrics
    if 'viewer_notes' not in df.columns:
        df['viewer_notes'] = 0
    
    if 'viewer_critiques' not in df.columns:
        df['viewer_critiques'] = 0
    
    if 'press_critics_count_num' not in df.columns:
        df['press_critics_count_num'] = 0
    
    return df

def add_date_features(df):
    """
    Add features related to release date
    """
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    
    df['release_date_france_year'] = df['release_date'].dt.year
    df['release_date_france_month'] = df['release_date'].dt.month
    df['release_date_france_day'] = df['release_date'].dt.day
    
    df['release_date_france_month'] = df['release_date_france_month'].map(
        lambda x: calendar.month_name[int(x)] if pd.notna(x) and x is not None else None
    )
    
    def get_season(month):
        if pd.isna(month) or month is None:
            return None
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        else:
            return 'Fall'
    
    df['release_season'] = df['release_date'].dt.month.apply(get_season)
    df['release_season_binary'] = df['release_season'].apply(
        lambda x: 1 if x in ['Summer', 'Winter'] else 0 if pd.notna(x) else None
    )
    
    df['release_date_binary'] = df['release_date'].dt.month.apply(
        lambda x: 1 if x in [5, 6, 7, 10, 11, 12] else 0 if pd.notna(x) else None
    )
    
    return df

def add_duration_features(df):
    """
    Add features related to movie duration
    """
    df['duration_binary'] = df['duration'].apply(
        lambda x: 1 if pd.notna(x) and x > 120 else 0
    )
    
    def categorize_duration(duration):
        if pd.isna(duration):
            return "normal-film"
        if duration < 70:
            return "short-film"
        elif 70 <= duration < 160:
            return "normal-film"
        elif 160 <= duration < 210:
            return "long-film"
        else:
            return "very long film"
    
    df['duration_classified'] = df['duration'].apply(categorize_duration)
    
    return df

def add_director_features(df):
    """
    Add features related to movie director
    """
    df['director_binary'] = df['director'].apply(
        lambda x: 1 if pd.notna(x) and x != '' and x is not None else 0
    )
    
    return df

def add_people_features(df):
    """
    Add features related to people involved (producers, stars)
    """
    df['producers_list'] = df['producers'].apply(parse_list_string)
    df['producers_count'] = df['producers_list'].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    df['producers_count_binary'] = df['producers_count'].apply(
        lambda x: 1 if x > 0 else 0
    )
    
    df['top_stars_list'] = df['top_stars'].apply(parse_list_string)
    df['top_stars_count'] = df['top_stars_list'].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    df['top_stars_count_binary'] = df['top_stars_count'].apply(
        lambda x: 1 if x > 0 else 0
    )
    
    return df

def add_cultural_features(df):
    """
    Add features related to cultural and language attributes
    """
    # Process languages_list
    df['languages_list'] = df['languages'].apply(parse_list_string)
    df['languages_count'] = df['languages_list'].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    
    # Process nationality_list
    df['nationality_list'] = df['film_nationality'].apply(parse_list_string)
    df['nationality_list_count'] = df['nationality_list'].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    df['nationality_list_binary'] = df['nationality_list'].apply(
        lambda x: 1 if isinstance(x, list) and any(nat.lower() == 'france' for nat in x) else 0
    )
    
    # Process associated_genres_list
    df['associated_genres_list'] = df['associated_genres'].apply(parse_list_string)
    df['associated_genres_count'] = df['associated_genres_list'].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    
    return df

def add_synopsis_features(df):
    """
    Add features related to synopsis and film details
    """
    # Process synopsis
    df['synopsis_length'] = df['synopsis'].apply(
        lambda x: len(str(x)) if pd.notna(x) else 0
    )
    df['synopsis_binary'] = df['synopsis_length'].apply(
        lambda x: 1 if x > 200 else 0
    )
    
    # Calculate synopsis sentiment
    df['synopsis_sentiment'] = df['synopsis'].apply(
        lambda x: TextBlob(str(x) if pd.notna(x) else "").sentiment.polarity
    )
    
    def categorize_synopsis_length(num):
        if pd.isna(num):
            return "not long"
        if num <= 200:
            return "not long"
        elif 200 < num < 700:
            return "normal"
        elif 700 < num < 1000:
            return "long"
        else:
            return "very long"
    
    def categorize_synopsis_sentiment(num):
        if pd.isna(num):
            return "neutral"
        if num <= -0.2:
            return "negative"
        elif -0.2 < num < 0.2:
            return "neutral"
        elif 0.2 < num < 0.5:
            return "positive"
        else:
            return "very positive"
    
    df['synopsis_length_categorized'] = df['synopsis_length'].apply(categorize_synopsis_length)
    df['synopisis_sentiment_categorized'] = df['synopsis_sentiment'].apply(categorize_synopsis_sentiment)
    
    df['filming_secrets_num'] = df['filming_secrets'].apply(
        lambda x: int(re.search(r'\d+', str(x)).group()) if pd.notna(x) and re.search(r'\d+', str(x)) else 0
    )
    
    if 'awards' in df.columns:
        
        df['award_count'] = df['awards'].apply(lambda x: 1 if pd.notna(x) and str(x).strip() != '' else 0)
        df['nomination_count'] = df['award_count']  
    else:
        df['award_count'] = 0
        df['nomination_count'] = 0
    
    
    df['award_binary'] = df['award_count'].apply(lambda num: 1 if num > 0 else 0)
    df['nomination_binary'] = df['nomination_count'].apply(lambda num: 1 if num > 0 else 0)
    
    if 'trailer_views' in df.columns:
        df['trailer_views_num'] = df['trailer_views'].apply(parse_trailer_views)
    else:
        df['trailer_views_num'] = 0
    
    df['trailer_views_num_binary'] = df['trailer_views_num'].apply(
        lambda x: 1 if x > 10000 else 0
    )
    
    return df

def add_distributor_features(df):
    """
    Add features related to movie distributor
    """
    # Distributor binary feature
    df['distributor_binary'] = df['distributor'].apply(
        lambda x: 1 if pd.notna(x) and x != '' else 0
    )
    
    # Define top distributors
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
    
    # Score top distributors
    df['top_distributor_score'] = df['distributor'].apply(
        lambda x: 1 if isinstance(x, str) and any(distributor.lower() in str(x).lower() for distributor in top_distributor) else 0.5
    )
    
    # Weight dictionaries for distributor power
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
            return 0
        
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

def parse_list_string(list_str):
    """
    Parse a string that contains a list of items
    Examples: "item1,item2,item3" or "[item1, item2, item3]"
    """
    if pd.isna(list_str) or list_str is None or list_str == '':
        return []
    
    # If it's already a list, return it
    if isinstance(list_str, list):
        return list_str
    
    # If it's a string representation of a list, parse it
    if isinstance(list_str, str):
        # Try to parse as a Python list literal first
        if list_str.startswith('[') and list_str.endswith(']'):
            try:
                return ast.literal_eval(list_str)
            except (SyntaxError, ValueError):
                pass
        
        # Split by comma and strip whitespace
        items = [item.strip() for item in list_str.split(',')]
        return [item for item in items if item]  # Remove empty items
    
    return []

def parse_trailer_views(views_str):
    """Parse trailer views string to number"""
    if pd.isna(views_str) or views_str is None:
        return 0
    
    if isinstance(views_str, (int, float)):
        return float(views_str)
    
    # Remove non-numeric characters and convert to number
    views_str = str(views_str)
    # Try to extract numbers
    num_match = re.findall(r'[\d\s.,]+', views_str)
    if num_match:
        # Join all matches and clean
        num_str = ''.join(num_match)
        # Replace common thousand separators
        num_str = num_str.replace(' ', '').replace(',', '').replace('.', '')
        try:
            return float(num_str)
        except ValueError:
            pass
    
    return 0

def add_studio_features(df):
    """
    Add features related to studio and production company
    """
    # Define studio categories
    major_studios = [
        'disney', 'warner', 'universal', 'sony', 'paramount',
        '20th century', 'fox', 'gaumont', 'pathé',
        'netflix', 'amazon', 'apple'
    ]
    
    french_majors = [
        'studiocanal', 'gaumont', 'pathé', 'ufp', 'snd', 'diaphana'
    ]
    
    # Create studio feature columns
    df['is_major_studio'] = df['distributor'].apply(
        lambda x: 1 if isinstance(x, str) and any(studio.lower() in x.lower() for studio in major_studios) else 0
    )
    
    df['is_french_major_studio'] = df['distributor'].apply(
        lambda x: 1 if isinstance(x, str) and any(fm.lower() in x.lower() for fm in french_majors) else 0
    )
    
    # Create composite features
    df['major_studio_and_licence'] = (df['is_major_studio'] & df['is_licence']).astype(int)
    df['french_major_and_licence'] = (df['is_french_major_studio'] & df['is_licence']).astype(int)
    
    return df

def add_interaction_features(df):
    
    df['major_studio_x_franchise'] = df['is_major_studio'] * df['franchise_level']
    
    df['is_connected_universe'] = (
        (df['is_superhero_franchise'] == 1) & 
        (df['franchise_level'] >= 2)
    ).astype(int)
    
    df['estimated_marketing_power'] = (
        df['franchise_level'] * 2 + df['is_major_studio'] * 1.5
    )
    
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