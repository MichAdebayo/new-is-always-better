from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import os
import logging
from typing import List, Dict, Any, Optional
from app.schema.movie_schema import MovieInput, MoviePrediction, BatchMovieInput, BatchMoviePrediction
from app.preprocessing.feature_engineering import preprocess_movie_data
from app.models.prediction_model import get_model_instance
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Movie Box Office Prediction API",
    description="API for predicting French box office entries for movies",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return {
        "message": "Movie Box Office Prediction API",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/predict", "method": "POST", "description": "Predict box office for a single movie"},
            {"path": "/predict_batch", "method": "POST", "description": "Predict box office for multiple movies"},
            {"path": "/predict_csv", "method": "POST", "description": "Upload a CSV file to get predictions"}
        ]
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Check if model can be loaded
        model = get_model_instance()
        return {"status": "healthy", "model_loaded": True}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

# Single movie prediction endpoint
@app.post("/predict", response_model=MoviePrediction, tags=["predictions"])
async def predict_movie(movie: MovieInput):
    try:
        logger.info(f"Received prediction request for movie: {movie.film_title}")
        
        # Convert to DataFrame
        movie_df = pd.DataFrame([movie.dict()])
        
        # Preprocess data
        processed_df = preprocess_movie_data(movie_df)
        logger.info(f"Preprocessing complete for movie: {movie.film_title}")
        
        # Get prediction
        model = get_model_instance()
        predictions = model.predict(processed_df)
        logger.info(f"Prediction complete for movie: {movie.film_title}")
        
        return predictions[0]
    
    except Exception as e:
        logger.error(f"Error predicting movie {movie.film_title}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# Batch prediction endpoint
@app.post("/predict_batch", response_model=BatchMoviePrediction, tags=["predictions"])
async def predict_batch(batch: BatchMovieInput):
    try:
        logger.info(f"Received batch prediction request for {len(batch.movies)} movies")
        
        # Convert to DataFrame
        movies_df = pd.DataFrame([movie.dict() for movie in batch.movies])
        
        # Preprocess data
        processed_df = preprocess_movie_data(movies_df)
        logger.info(f"Preprocessing complete for batch of {len(batch.movies)} movies")
        
        # Get predictions
        model = get_model_instance()
        predictions = model.predict(processed_df)
        logger.info(f"Prediction complete for batch of {len(batch.movies)} movies")
        
        return {"predictions": predictions}
    
    except Exception as e:
        logger.error(f"Error predicting batch of movies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

# CSV upload endpoint
@app.post("/predict_csv", response_model=BatchMoviePrediction, tags=["predictions"])
async def predict_csv(file: UploadFile = File(...)):
    try:
        logger.info(f"Received CSV prediction request: {file.filename}")
        
        # Read CSV
        contents = await file.read()
        
        # Debug the raw CSV content
        csv_content = contents.decode('utf-8')
        logger.info(f"CSV Content first 100 chars: {csv_content[:100]}")
        
        # Read CSV with correct parameters
        csv_df = pd.read_csv(
            io.StringIO(csv_content),
            sep=',',          
            quotechar='"',    
            encoding='utf-8'  
        )
        
        # Debug the DataFrame columns and first row
        logger.info(f"CSV columns: {csv_df.columns.tolist()}")
        if not csv_df.empty:
            logger.info(f"First row film_title: {csv_df['film_title'].iloc[0]}")
        
        logger.info(f"CSV loaded with {len(csv_df)} movies")
        
        # Preprocess data
        processed_df = preprocess_movie_data(csv_df)
        logger.info(f"Preprocessing complete for CSV with {len(csv_df)} movies")
        
        # Get predictions
        model = get_model_instance()
        predictions = model.predict(processed_df)
        logger.info(f"Prediction complete for CSV with {len(csv_df)} movies")
        
        return {"predictions": predictions}
    
    except Exception as e:
        logger.error(f"Error predicting from CSV {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CSV prediction error: {str(e)}")
    
# Sample data endpoint for demonstration
@app.get("/sample", tags=["utilities"])
async def get_sample():
    return {
        "sample_input": {
            "film_title": "Avatar 3",
            "release_date": "2025-12-25",
            "duration": "2h 45min",
            "age_classification": "Tout public",
            "producers": "James Cameron,Jon Landau",
            "director": "James Cameron",
            "top_stars": "Sam Worthington,Zoe Saldana,Sigourney Weaver",
            "languages": "Anglais",
            "distributor": "20th Century Studios",
            "year_of_production": "2025",
            "film_nationality": "États-Unis",
            "filming_secrets": "15 anecdotes",
            "awards": "",
            "associated_genres": "Science-Fiction,Aventure",
            "broadcast_category": "en salle",
            "trailer_views": "5000000 vues",
            "synopsis": "Jake Sully et Neytiri sont de retour pour une nouvelle aventure épique sur Pandora, confrontés à de nouveaux défis qui menacent leur peuple et leur planète."
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


def parse_duration(duration_str):
    """Parse duration string like '1h 44min' to minutes"""
    if pd.isna(duration_str) or duration_str is None:
        return 105  
    
    if isinstance(duration_str, (int, float)):
        return float(duration_str)
    
    total_minutes = 0
    
    hours_match = re.search(r'(\d+)h', str(duration_str))
    if hours_match:
        total_minutes += int(hours_match.group(1)) * 60
    
    minutes_match = re.search(r'(\d+)min', str(duration_str))
    if minutes_match:
        total_minutes += int(minutes_match.group(1))
    
    if total_minutes == 0:
        number_match = re.search(r'(\d+)', str(duration_str))
        if number_match:
            total_minutes = int(number_match.group(1))
    
    return total_minutes if total_minutes > 0 else 105