import os
import logging
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Union
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_directory_exists(directory_path: Union[str, Path]) -> None:
    """
    Ensure that a directory exists, creating it if necessary
    
    Args:
        directory_path: Path to the directory
    """
    directory = Path(directory_path)
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def save_predictions_to_csv(predictions: List[Dict[str, Any]], output_path: Union[str, Path]) -> None:
    """
    Save predictions to a CSV file
    
    Args:
        predictions: List of prediction dictionaries
        output_path: Path to save the CSV file
    """
    try:
        # Create DataFrame from predictions
        df = pd.DataFrame([
            {
                'film_title': p['film_title'],
                'predicted_fr_entries': p['predicted_fr_entries']
            } for p in predictions
        ])
        
        # Ensure the directory exists
        ensure_directory_exists(os.path.dirname(output_path))
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        logger.info(f"Saved predictions to {output_path}")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error saving predictions to CSV: {str(e)}")
        raise e

def format_results_for_frontend(predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format prediction results in a way that's suitable for frontend visualization
    
    Args:
        predictions: List of prediction dictionaries
    
    Returns:
        Dictionary with formatted data for frontend
    """
    try:
        formatted = {
            "movies": [],
            "total_predicted_entries": 0,
            "average_predicted_entries": 0
        }
        
        total_entries = 0
        for p in predictions:
            formatted["movies"].append({
                "title": p["film_title"],
                "entries": p["predicted_fr_entries"],
                "formatted_entries": f"{p['predicted_fr_entries']:,}".replace(",", " ")
            })
            total_entries += p["predicted_fr_entries"]
        
        formatted["total_predicted_entries"] = total_entries
        formatted["average_predicted_entries"] = total_entries / len(predictions) if predictions else 0
        
        return formatted
    
    except Exception as e:
        logger.error(f"Error formatting results for frontend: {str(e)}")
        return {"error": str(e)}

def load_sample_data() -> pd.DataFrame:
    """
    Load a sample dataset for testing purposes
    
    Returns:
        DataFrame with sample movie data
    """
    # Sample data dictionary
    sample_data = {
        "film_title": ["Avatar 3", "The Avengers: Secret Wars", "Mission Impossible 8"],
        "release_date": ["2025-12-25", "2026-05-01", "2025-06-15"],
        "duration": ["2h 45min", "2h 30min", "2h 15min"],
        "age_classification": ["Tout public", "Tout public", "Tout public"],
        "producers": ["James Cameron,Jon Landau", "Kevin Feige", "Tom Cruise,Christopher McQuarrie"],
        "director": ["James Cameron", "Anthony Russo,Joe Russo", "Christopher McQuarrie"],
        "top_stars": ["Sam Worthington,Zoe Saldana", "Robert Downey Jr.,Chris Evans", "Tom Cruise,Simon Pegg"],
        "languages": ["Anglais", "Anglais", "Anglais"],
        "distributor": ["20th Century Studios", "Walt Disney Pictures", "Paramount Pictures"],
        "year_of_production": ["2025", "2026", "2025"],
        "film_nationality": ["États-Unis", "États-Unis", "États-Unis"],
        "filming_secrets": ["15 anecdotes", "10 anecdotes", "12 anecdotes"],
        "awards": ["", "", ""],
        "associated_genres": ["Science-Fiction,Aventure", "Action,Super-héros", "Action,Espionnage"],
        "broadcast_category": ["en salle", "en salle", "en salle"],
        "trailer_views": ["5000000 vues", "8000000 vues", "3500000 vues"],
        "synopsis": [
            "Jake Sully et Neytiri sont de retour pour une nouvelle aventure épique sur Pandora.",
            "Les Avengers se réunissent pour combattre une nouvelle menace cosmique.",
            "Ethan Hunt se trouve confronté à sa mission la plus dangereuse."
        ]
    }
    
    return pd.DataFrame(sample_data)