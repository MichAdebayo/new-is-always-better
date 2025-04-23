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
    # If input is a dictionary, convert to DataFrame
    if isinstance(movie_data, dict):
        df = pd.DataFrame([movie_data])
    else:
        df = pd.DataFrame(movie_data)
    
    if isinstance(movie_data, list):
        df = pd.DataFrame(movie_data)
    
    required_columns = [
        'film_title', 'release_date', 'duration', 'director', 
        'distributor', 'year_of_production', 'synopsis', 
        'broadcast_category', 'top_stars', 'producers',
        'languages', 'film_nationality', 'associated_genres',
        'trailer_views', 'filming_secrets'
    ]
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    
    # Transform and add empty columns for any missing expected columns
    df = transform_basic_features(df)
    
    # Add all the engineered features
    df = add_date_features(df)
    df = add_duration_features(df)
    df = add_director_features(df)
    df = add_people_features(df)
    df = add_cultural_features(df)
    df = add_synopsis_features(df)
    df = add_distributor_features(df)
    df = add_franchise_features(df)
    df = add_licence_features(df)
    df = add_studio_features(df)
    df = add_interaction_features(df)
    
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

def add_franchise_features(df):
    """
    Add features related to movie franchise status
    """
    # Define franchise lists
    top_franchises = [
        'mad max', 'iron man', 'captain america', 'thor', 'wolverine',
        'mission impossible', 'terminator', 'hunger games', 'twilight',
        'pirates des caraïbes', 'le hobbit', 'matrix', 'minecraft',
        'les minions', 'john wick', 'alien', 'predator', 'rocky', 'rambo',
        'conjuring', 'saw', 'scream', 'halloween', 'barbie',
        'harry potter', 'star wars', 'spider-man', 'avengers', 'x-men',
        'batman', 'jurassic', 'fast and furious', 'transformers',
        'le seigneur des anneaux', 'shrek', 'le roi lion', 'indiana jones',
        "l'âge de glace", 'deadpool', 'super mario bros', 'les animaux fantastiques',
        'avatar', 'les dents de la', 'les gardiens de la galaxie'
    ]
    
    # Mega franchises
    mega_franchises = [
        'avatar', 'jurassic', 'star wars', 'harry potter',
        'avengers', 'fast and furious', 'le roi lion', 'spider-man'
    ]
    
    # Major franchises
    major_franchises = [
        'iron man', 'captain america', 'x-men', 'batman',
        'transformers', 'deadpool', 'les minions', 'moi moche et méchant',
        'mission impossible', 'shrek', 'le seigneur des anneaux', "l'âge de glace",
        'super mario bros'
    ]
    
    # Big franchises
    big_franchises = [
        'mad max', 'hunger games', 'twilight', 'john wick', 'thor', 'wolverine',
        'matrix', 'pirates des caraïbes', 'le hobbit', 'conjuring',
        'les animaux fantastiques', 'indiana jones', 'les gardiens de la galaxie',
        'minecraft', 'rocky', 'rambo', 'alien', 'predator',
        'scream', 'saw', 'halloween', 'barbie', 'terminator', 'les dents de la'
    ]
    
    # Detection function using franchise level
    def identify_franchise_level(title, top_franchises):
        # Return the franchise power level (0 to 4) based on the film title.
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
    
    df['franchise_level'] = df['film_title'].apply(lambda x: identify_franchise_level(x, top_franchises))
    
    # MCU titles
    mcu_titles = [
        'avengers', 'iron man', 'captain america', 'thor', 'hulk',
        'black panther', 'doctor strange', 'les gardiens de la galaxie',
        'ant-man', 'spider-man', 'les eternels', 'shang-chi', 'black widow',
        'marvels', 'wanda', 'vision', 'falcon', "le soldat de l'hiver"
    ]
    
    df['is_mcu'] = df['film_title'].apply(
        lambda x: 1 if isinstance(x, str) and any(title in x.lower() for title in mcu_titles) else 0
    )
    
    # Likely blockbusters
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
    
    # Calculate franchise blockbuster score
    def calculate_franchise_blockbuster_score(row):
        # 1. Base score from franchise level
        base_score = row['franchise_level'] * 2
        
        # 2. Bonus for each franchise category
        bonus_score = sum([
            row.get('is_superhero_franchise', 0),
            row.get('is_animation_franchise', 0),
            row.get('is_action_franchise', 0),
            row.get('is_gaming_franchise', 0),
            row.get('is_sequel', 0)
        ])
        
        # 3. Bonus for "strong" distributors
        strong_distributors = [
            'warner', 'disney', 'universal', 'paramount', 
            'sony', '20th century', 'pathé', 'gaumont', 'netflix'
        ]
        
        dist_bonus = 0
        if isinstance(row.get('distributor'), str):
            dist_bonus = 1 if any(sd.lower() in row['distributor'].lower() for sd in strong_distributors) else 0
        
        # 4. Combine everything
        return base_score + bonus_score + dist_bonus
    
    # We'll calculate this after adding the licence features
    
    return df

def add_licence_features(df):
    
    superhero_franchises = [
        'marvel', 'avengers', 'captain america', 'iron man', 'thor', 'hulk',
        'batman', 'superman', 'dc', 'justice league', 'x-men', 'spider-man',
        'wolverine', 'deadpool', 'les gardiens de la galaxie'
    ]
    
    animation_franchises = [
        'disney', 'pixar', 'dreamworks', 'illumination', 'vaiana', 'astérix',
        'shrek', 'toy story', 'madagascar', 'minions', 'vice-versa',
        'moi, moche et méchant', "l'âge de glace", 'le roi lion', 'super mario bros'
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
        "assassin's creed", 'sonic', 'mortal kombat', 'uncharted', 'warcraft'
    ]
    
    
    def contains_any(text, keywords):
        if not isinstance(text, str):
            return False
        text = text.lower()
        return any(f in text for f in keywords)
    
    df['is_superhero_franchise'] = df['film_title'].apply(
        lambda x: int(contains_any(x, superhero_franchises)) if pd.notna(x) else 0
    )
    
    df['is_animation_franchise'] = df['film_title'].apply(
        lambda x: int(contains_any(x, animation_franchises)) if pd.notna(x) else 0
    )
    
    df['is_action_franchise'] = df['film_title'].apply(
        lambda x: int(contains_any(x, action_franchises)) if pd.notna(x) else 0
    )
    
    df['is_gaming_franchise'] = df['film_title'].apply(
        lambda x: int(contains_any(x, gaming_franchises)) if pd.notna(x) else 0
    )
    
    df['is_licence'] = (
        df['is_superhero_franchise'] | 
        df['is_animation_franchise'] | 
        df['is_action_franchise'] | 
        df['is_gaming_franchise']
    ).astype(int)
    
    sequel_indicators = [
        '2', '3', '4', '5', 'ii', 'iii', 'iv', 'v', 'vi', 
        'le retour', 'la suite', 'chapitre', 'épisode', 'saga', 
        'partie', 'part', 'volume'
    ]
    
    df['is_sequel'] = df['film_title'].apply(
        lambda x: int(contains_any(x, sequel_indicators)) if pd.notna(x) else 0
    )
    
    # Now calculate franchise_blockbuster_score
    # 1. Base score from franchise level
    base_score = df['franchise_level'] * 2
    
    # 2. Bonus for each franchise category
    bonus_cols = [
        'is_superhero_franchise',
        'is_animation_franchise',
        'is_action_franchise',
        'is_gaming_franchise',
        'is_sequel'
    ]
    bonus_score = df[bonus_cols].sum(axis=1)
    
    # 3. Bonus for "strong" distributors
    strong_distributors = [
        'warner', 'disney', 'universal', 'paramount', 
        'sony', '20th century', 'pathé', 'gaumont', 'netflix'
    ]
    
    dist_bonus = df['distributor'].apply(
        lambda x: 1 if isinstance(x, str) and any(sd.lower() in x.lower() for sd in strong_distributors) else 0
    )
    
    # 4. Combine everything
    df['franchise_blockbuster_score'] = base_score + bonus_score + dist_bonus
    
    return df

def parse_duration(duration_str):
    """Parse duration string like '1h 44min' to minutes"""
    if pd.isna(duration_str) or duration_str is None:
        return 105  # Default duration
    
    if isinstance(duration_str, (int, float)):
        return float(duration_str)
    
    total_minutes = 0
    
    # Extract hours
    hours_match = re.search(r'(\d+)h', str(duration_str))
    if hours_match:
        total_minutes += int(hours_match.group(1)) * 60
    
    # Extract minutes
    minutes_match = re.search(r'(\d+)min', str(duration_str))
    if minutes_match:
        total_minutes += int(minutes_match.group(1))
    
    # If no pattern matched but there's a number, assume it's minutes
    if total_minutes == 0:
        number_match = re.search(r'(\d+)', str(duration_str))
        if number_match:
            total_minutes = int(number_match.group(1))
    
    # If still zero, use default
    return total_minutes if total_minutes > 0 else 105


def parse_year(year_str):
    """Parse year string to integer"""
    if pd.isna(year_str) or year_str is None:
        return None
    
    if isinstance(year_str, (int, float)):
        return int(year_str)
    
    year_match = re.search(r'(\d{4})', str(year_str))
    if year_match:
        return int(year_match.group(1))
    
    return datetime.now().year

def get_iso_week(date_str):
    """Get ISO week number from date string"""
    if pd.isna(date_str) or date_str is None:
        return None
    
    if isinstance(date_str, str):
        try:
            date = pd.to_datetime(date_str)
            return date.isocalendar()[1]  # Week number
        except:
            return None
    
    if isinstance(date_str, pd.Timestamp):
        return date_str.isocalendar()[1]
    
    return None

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