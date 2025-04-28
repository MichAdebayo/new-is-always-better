# main.py
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import os
import sys
import logging
import traceback
from typing import List, Dict, Any, Optional
# from app.schema.movie_schema import MovieInput, MoviePrediction, BatchMovieInput, BatchMoviePrediction
from app.preprocessing.feature_engineering import preprocess_movie_data
# from app.models.prediction_model import get_model_instance
import re
from app.models.prediction_model import MoviePredictionModel

from app.models import prediction_model
import importlib
importlib.reload(prediction_model)

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("api.log")
    ]
)
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

# # Health check endpoint
# @app.get("/health")
# async def health_check():
#     try:
#         # Check if model can be loaded
#         model = get_model_instance()
#         return {"status": "healthy", "model_loaded": True}
#     except Exception as e:
#         logger.error(f"Health check failed: {str(e)}")
#         return {"status": "unhealthy", "error": str(e)}

# def parse_duration(duration_str):
#     """Parse duration string like '1h 44min' to minutes"""
#     if pd.isna(duration_str) or duration_str is None:
#         return 105  
    
#     if isinstance(duration_str, (int, float)):
#         return float(duration_str)
    
#     total_minutes = 0
    
#     hours_match = re.search(r'(\d+)h', str(duration_str))
#     if hours_match:
#         total_minutes += int(hours_match.group(1)) * 60
    
#     minutes_match = re.search(r'(\d+)min', str(duration_str))
#     if minutes_match:
#         total_minutes += int(minutes_match.group(1))
    
#     if total_minutes == 0:
#         number_match = re.search(r'(\d+)', str(duration_str))
#         if number_match:
#             total_minutes = int(number_match.group(1))
    
#     return total_minutes if total_minutes > 0 else 105

# # Single movie prediction endpoint
# @app.post("/predict", response_model=MoviePrediction, tags=["predictions"])
# async def predict_movie(movie_input: MovieInput):
#     try:
#         logger.info(f"Received prediction request for movie: {movie_input.film_title}")
        
#         # Convertir les données d'entrée en dictionnaire
#         movie_dict = movie_input.dict()
#         logger.info(f"Input data: {movie_dict}")
        
#         # Traiter la durée si elle est au format "Xh Ymin"
#         if movie_dict.get('duration') and isinstance(movie_dict['duration'], str):
#             movie_dict['duration'] = parse_duration(movie_dict['duration'])
#             logger.info(f"Parsed duration: {movie_dict['duration']}")
        
#         # Convertir en DataFrame
#         movie_df = pd.DataFrame([movie_dict])
        
#         # Prétraiter les données avec gestion des erreurs
#         try:
#             processed_df = preprocess_movie_data(movie_df)
#             logger.info(f"Preprocessing complete for movie: {movie_input.film_title}")
#             logger.debug(f"Processed columns: {processed_df.columns.tolist()}")
#         except Exception as preprocess_error:
#             logger.error(f"Preprocessing error: {str(preprocess_error)}")
#             logger.error(traceback.format_exc())
#             raise HTTPException(
#                 status_code=500, 
#                 detail=f"Preprocessing error: {str(preprocess_error)}"
#             )
        
#         # Obtenir la prédiction
#         try:
#             model = get_model_instance()
#             predictions = model.predict(processed_df)
#             logger.info(f"Prediction complete for movie: {movie_input.film_title}")
#             logger.info(f"Prediction result: {predictions[0]}")
#             return predictions[0]
#         except Exception as predict_error:
#             logger.error(f"Prediction error: {str(predict_error)}")
#             logger.error(traceback.format_exc())
#             raise HTTPException(
#                 status_code=500, 
#                 detail=f"Model prediction error: {str(predict_error)}"
#             )
    
#     except Exception as e:
#         logger.error(f"Error predicting movie {movie_input.film_title}: {str(e)}")
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

# Batch prediction endpoint
# @app.post("/predict_batch", response_model=BatchMoviePrediction, tags=["predictions"])
# async def predict_batch(batch: BatchMovieInput):
#     try:
#         logger.info(f"Received batch prediction request for {len(batch.movies)} movies")
        
#         # Convert to DataFrame
#         movies_dicts = []
#         for movie in batch.movies:
#             movie_dict = movie.dict()
#             if movie_dict.get('duration') and isinstance(movie_dict['duration'], str):
#                 movie_dict['duration'] = parse_duration(movie_dict['duration'])
#             movies_dicts.append(movie_dict)
        
#         movies_df = pd.DataFrame(movies_dicts)
        
#         # Preprocess data
#         processed_df = preprocess_movie_data(movies_df)
#         logger.info(f"Preprocessing complete for batch of {len(batch.movies)} movies")
        
#         # Get predictions
#         model = get_model_instance()
#         predictions = model.predict(processed_df)
#         logger.info(f"Prediction complete for batch of {len(batch.movies)} movies")
        
#         return {"predictions": predictions}
    
#     except Exception as e:
#         logger.error(f"Error predicting batch of movies: {str(e)}")
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

# @app.post("/predict_csv", response_model=BatchMoviePrediction, tags=["predictions"])
@app.post("/predict_csv", tags=["predictions"])
async def predict_csv(file: UploadFile = File(...)):
    try:
        logger.info(f"Received CSV prediction request: {file.filename}")
        
        # Read CSV
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        logger.info(f"CSV Content first 100 chars: {csv_content[:100]}")
        
        # Parse CSV
        try:
            csv_df = pd.read_csv(
                io.StringIO(csv_content),
                sep=',',
                quotechar='"',
                encoding='utf-8'
            )
        except Exception as csv_error:
            logger.error(f"CSV parsing error: {str(csv_error)}")
            raise HTTPException(
                status_code=400,
                detail=f"CSV parsing error: {str(csv_error)}"
            )
        
        logger.info(f"CSV columns: {csv_df.columns.tolist()}")
        if not csv_df.empty:
            logger.info(f"First row film_title: {csv_df['film_title'].iloc[0]}")
        
        logger.info(f"CSV loaded with {len(csv_df)} movies")
        
        # Create an instance of the MoviePredictionModel
        model = MoviePredictionModel()

        # Step 1: Preprocess the raw data
        raw_df = preprocess_movie_data(csv_df)
        logger.info(f"Viewing raw dataframe columns: {raw_df.columns.tolist()}")

        # Step 2: Add list-based columns
        list_added_df = model.create_list_based_features(raw_df)

        # Step 3: Filter the data for prediction
        filtered_df = model.create_data_for_prediction(list_added_df)
        
        # Step 4: Preprocess the filtered data
        cleaned_df = model._preprocess_dataframe(filtered_df)

        # Step 5: Make predictions
        cleaned_df_copy = cleaned_df.drop(columns=['film_title'], axis=1)

        cleaned_final_df = cleaned_df_copy.copy().rename(columns={"lang_Français": "lang_Fran_ais",
                                                             "lang_Hébreu" : "lang_H_breu",
                                                             "nat_Grande-Bretagne" : "nat_Grande_Bretagne",
                                                             "nat_Nouvelle-Zélande" : "nat_Nouvelle_Z_lande",
                                                             "nat_U.S.A." : "nat_U_S_A_",
                                                             "star_André Dussollier" : "star_Andr__Dussollier",
                                                             "star_Jean-Paul Rouve" : "star_Jean_Paul_Rouve",
                                                             "star_Benoît Poelvoorde" : "star_Beno_t_Poelvoorde",
                                                             "star_Brad Pitt" : "star_Brad_Pitt",
                                                             "star_Chris Evans" : "star_Chris_Evans",
                                                             "star_Chris Pratt": "star_Chris_Pratt",
                                                            "star_Christian Clavier": "star_Christian_Clavier",
                                                            "star_Clovis Cornillac": "star_Clovis_Cornillac",
                                                            "star_Daniel Craig": "star_Daniel_Craig",
                                                            "star_Daniel Radcliffe": "star_Daniel_Radcliffe",
                                                            "star_Dany Boon": "star_Dany_Boon",
                                                            "star_Dwayne Johnson": "star_Dwayne_Johnson",
                                                            "star_Emma Watson": "star_Emma_Watson",
                                                            "star_Ewan McGregor": "star_Ewan_McGregor",
                                                            "star_Franck Dubosc": "star_Franck_Dubosc",
                                                            "star_Gad Elmaleh": "star_Gad_Elmaleh",
                                                            "star_George Clooney": "star_George_Clooney",
                                                            "star_Gilles Lellouche": "star_Gilles_Lellouche",
                                                            "star_Guillaume Canet": "star_Guillaume_Canet",
                                                            "star_Gérard Depardieu": "star_G_rard_Depardieu",
                                                            "star_Gérard Lanvin": "star_G_rard_Lanvin",
                                                            "star_Hugh Jackman": "star_Hugh_Jackman",
                                                            "star_Isabelle Nanty": "star_Isabelle_Nanty",
                                                            "star_Jamel Debbouze": "star_Jamel_Debbouze",
                                                            "star_Jason Statham": "star_Jason_Statham",
                                                            "star_Jean Dujardin": "star_Jean_Dujardin",
                                                            "star_Jean Reno": "star_Jean_Reno",
                                                            "star_Johnny Depp": "star_Johnny_Depp",
                                                            "star_José Garcia": "star_Jos__Garcia",
                                                            "star_Kad Merad": "star_Kad_Merad",
                                                            "star_Keira Knightley": "star_Keira_Knightley",
                                                            "star_Kristen Stewart": "star_Kristen_Stewart",
                                                            "star_Leonardo DiCaprio": "star_Leonardo_DiCaprio",
                                                            "star_Marion Cotillard": "star_Marion_Cotillard",
                                                            "star_Mark Ruffalo": "star_Mark_Ruffalo",
                                                            "star_Matt Damon": "star_Matt_Damon",
                                                            "star_Robert Downey Jr.": "star_Robert_Downey_Jr_",
                                                            "star_Robert Pattinson": "star_Robert_Pattinson",
                                                            "star_Rupert Grint": "star_Rupert_Grint",
                                                            "star_Ryan Reynolds": "star_Ryan_Reynolds",
                                                            "star_Steve Carell": "star_Steve_Carell",
                                                            "star_Tom Cruise": "star_Tom_Cruise",
                                                            "star_Tom Hanks": "star_Tom_Hanks",
                                                            "star_Vin Diesel": "star_Vin_Diesel",
                                                            "star_Vincent Cassel": "star_Vincent_Cassel",
                                                            "star_Will Smith": "star_Will_Smith",
                                                            "star_Zoe Saldana": "star_Zoe_Saldana",
                                                            
                                                            "prod_Anthony Russo": "prod_Anthony_Russo",
                                                            "prod_Chris Morgan": "prod_Chris_Morgan",
                                                            "prod_Christopher Markus": "prod_Christopher_Markus",
                                                            "prod_Christopher Nolan": "prod_Christopher_Nolan",
                                                            "prod_Clint Eastwood": "prod_Clint_Eastwood",
                                                            "prod_Dany Boon": "prod_Dany_Boon",
                                                            "prod_David Koepp": "prod_David_Koepp",
                                                            "prod_David Yates": "prod_David_Yates",
                                                            "prod_Fabien Onteniente": "prod_Fabien_Onteniente",
                                                            "prod_Franck Dubosc": "prod_Franck_Dubosc",
                                                            "prod_Gore Verbinski": "prod_Gore_Verbinski",
                                                            "prod_Guillaume Canet": "prod_Guillaume_Canet",
                                                            "prod_J.J. Abrams": "prod_J_J__Abrams",
                                                            "prod_Jeff Nathanson": "prod_Jeff_Nathanson",
                                                            "prod_Joe Russo": "prod_Joe_Russo",
                                                            "prod_Jon Favreau": "prod_Jon_Favreau",
                                                            "prod_Jonathan Aibel": "prod_Jonathan_Aibel",
                                                            "prod_Luc Besson": "prod_Luc_Besson",
                                                            "prod_Melissa Rosenberg": "prod_Melissa_Rosenberg",
                                                            "prod_Neal Purvis": "prod_Neal_Purvis",
                                                            "prod_Olivier Baroux": "prod_Olivier_Baroux",
                                                            "prod_Peter Jackson": "prod_Peter_Jackson",
                                                            "prod_Philippa Boyens": "prod_Philippa_Boyens",
                                                            "prod_Philippe de Chauveron": "prod_Philippe_de_Chauveron",
                                                            "prod_Rick Jaffa": "prod_Rick_Jaffa",
                                                            "prod_Ridley Scott": "prod_Ridley_Scott",
                                                            "prod_Sam Raimi": "prod_Sam_Raimi",
                                                            "prod_Simon Kinberg": "prod_Simon_Kinberg",
                                                            "prod_Stephen McFeely": "prod_Stephen_McFeely",
                                                            "prod_Steve Kloves": "prod_Steve_Kloves",
                                                            "prod_Steven Spielberg": "prod_Steven_Spielberg",
                                                            "prod_Ted Elliott": "prod_Ted_Elliott",
                                                            "prod_Terry Rossio": "prod_Terry_Rossio",
                                                            "prod_Tim Burton": "prod_Tim_Burton"


                                                            })

        # nat_Grande-Bretagne: Optional[int] = None
        # nat_Nouvelle-Zélande: Optional[int] = None
        # nat_U.S.A.: Optional[int] = None
        # star_Jean-Paul_Rouve: Optional[int] = None
        # star_Robert_Downey_Jr.: Optional[int] = None*

        # Afficher toutes les colonnes et leurs types
        num_columns = cleaned_final_df.columns.tolist()
        column_types = cleaned_final_df.dtypes.to_list()

        # Créer un DataFrame pour afficher les colonnes et leurs types
        dat_types = pd.DataFrame(
            {"Column Name": num_columns,
            "Data Type": column_types
            })

        # Ajuster les paramètres d'affichage pour afficher toutes les colonnes
        pd.set_option('display.max_rows', None)  # Afficher toutes les lignes
        pd.set_option('display.max_columns', None)  # Afficher toutes les colonnes
        pd.set_option('display.width', 1000)  # Ajuster la largeur de l'affichage
        pd.set_option('display.colheader_justify', 'left')  # Justifier les en-têtes à gauche

        # Afficher le DataFrame
        print(dat_types)

        # Réinitialiser les options si nécessaire
        pd.reset_option('display.max_rows')
        pd.reset_option('display.max_columns')
        pd.reset_option('display.width')
        pd.reset_option('display.colheader_justify')

        model_instance = model.load_model()
        predictions = model_instance.predict(cleaned_final_df)
        logger.info(f"Prediction complete for CSV with {len(csv_df)} movies")
        
        film_titles = cleaned_df['film_title'].tolist()
        predictions = predictions.tolist()

        response_data = {
            "Film titles": film_titles,
            "Predictions": predictions,
        }
    
        # Format the predictions into the expected response model
        # response = BatchMoviePrediction(
        #     predictions=[
        #         MoviePrediction(
        #             film_title=row['film_title'],
        #             prediction=prediction
        #         )
        #         for row, prediction in zip(csv_df.to_dict(orient='records'), predictions)
        #     ]
        # )
        
        return response_data

    except Exception as e:
        logger.error(f"Error predicting from CSV {file.filename}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"CSV prediction error: {str(e)}")
    


    #######################################################################################


@app.post("/predict_json", tags=["predictions"])
async def predict_json(request_data: dict):
    try:
        logger.info(f"Received JSON prediction request")
        logger.info(f"JSON Content first 100 chars: {str(request_data)[:100]}")
        
        # Extract the movie data from the request
        movies_data = None
        if 'movies' in request_data and isinstance(request_data['movies'], list):
            movies_data = request_data['movies']
        else:
            # Assume the data is directly a movie object
            movies_data = [request_data]
        
        logger.info(f"Found {len(movies_data)} movies in the request")
        
        # Convert JSON movies to DataFrame
        try:
            # Create DataFrame from JSON list
            json_df = pd.DataFrame(movies_data)
            
            # Verify that all required columns exist
            logger.info(f"JSON DataFrame columns: {json_df.columns.tolist()}")
            
            # Check if 'film_title' exists
            if 'film_title' not in json_df.columns:
                raise ValueError("Input JSON must contain 'film_title' field for each movie")
            
            # Convert DataFrame to CSV in memory
            csv_buffer = io.StringIO()
            json_df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()
            csv_buffer.seek(0)
            
            # Parse the CSV
            csv_df = pd.read_csv(
                csv_buffer,
                sep=',',
                quotechar='"',
                encoding='utf-8'
            )
            
        except Exception as parsing_error:
            logger.error(f"JSON/CSV parsing error: {str(parsing_error)}")
            raise HTTPException(
                status_code=400,
                detail=f"Data parsing error: {str(parsing_error)}"
            )
        
        logger.info(f"CSV columns: {csv_df.columns.tolist()}")
        if not csv_df.empty:
            logger.info(f"First film_title: {csv_df['film_title'].iloc[0]}")
        
        logger.info(f"Data loaded with {len(csv_df)} movies")
        
        # Continue with the rest of your code for model processing and prediction
        # ...
        
        # Create an instance of the MoviePredictionModel
        model = MoviePredictionModel()

        # Step 1: Preprocess the raw data
        raw_df = preprocess_movie_data(csv_df)
        logger.info(f"Viewing raw dataframe columns: {raw_df.columns.tolist()}")

        # Step 2: Add list-based columns
        list_added_df = model.create_list_based_features(raw_df)

        # Step 3: Filter the data for prediction
        filtered_df = model.create_data_for_prediction(list_added_df)
        
        # Step 4: Preprocess the filtered data
        cleaned_df = model._preprocess_dataframe(filtered_df)

        # Step 5: Make predictions
        cleaned_df_copy = cleaned_df.drop(columns=['film_title'], axis=1)

        # Column renaming remains the same
        cleaned_final_df = cleaned_df_copy.copy().rename(columns={"lang_Français": "lang_Fran_ais",
                                                             "lang_Hébreu" : "lang_H_breu",
                                                             "nat_Grande-Bretagne" : "nat_Grande_Bretagne",
                                                             "nat_Nouvelle-Zélande" : "nat_Nouvelle_Z_lande",
                                                             "nat_U.S.A." : "nat_U_S_A_",
                                                             "star_André Dussollier" : "star_Andr__Dussollier",
                                                             "star_Jean-Paul Rouve" : "star_Jean_Paul_Rouve",
                                                             "star_Benoît Poelvoorde" : "star_Beno_t_Poelvoorde",
                                                             "star_Brad Pitt" : "star_Brad_Pitt",
                                                             "star_Chris Evans" : "star_Chris_Evans",
                                                             "star_Chris Pratt": "star_Chris_Pratt",
                                                            "star_Christian Clavier": "star_Christian_Clavier",
                                                            "star_Clovis Cornillac": "star_Clovis_Cornillac",
                                                            "star_Daniel Craig": "star_Daniel_Craig",
                                                            "star_Daniel Radcliffe": "star_Daniel_Radcliffe",
                                                            "star_Dany Boon": "star_Dany_Boon",
                                                            "star_Dwayne Johnson": "star_Dwayne_Johnson",
                                                            "star_Emma Watson": "star_Emma_Watson",
                                                            "star_Ewan McGregor": "star_Ewan_McGregor",
                                                            "star_Franck Dubosc": "star_Franck_Dubosc",
                                                            "star_Gad Elmaleh": "star_Gad_Elmaleh",
                                                            "star_George Clooney": "star_George_Clooney",
                                                            "star_Gilles Lellouche": "star_Gilles_Lellouche",
                                                            "star_Guillaume Canet": "star_Guillaume_Canet",
                                                            "star_Gérard Depardieu": "star_G_rard_Depardieu",
                                                            "star_Gérard Lanvin": "star_G_rard_Lanvin",
                                                            "star_Hugh Jackman": "star_Hugh_Jackman",
                                                            "star_Isabelle Nanty": "star_Isabelle_Nanty",
                                                            "star_Jamel Debbouze": "star_Jamel_Debbouze",
                                                            "star_Jason Statham": "star_Jason_Statham",
                                                            "star_Jean Dujardin": "star_Jean_Dujardin",
                                                            "star_Jean Reno": "star_Jean_Reno",
                                                            "star_Johnny Depp": "star_Johnny_Depp",
                                                            "star_José Garcia": "star_Jos__Garcia",
                                                            "star_Kad Merad": "star_Kad_Merad",
                                                            "star_Keira Knightley": "star_Keira_Knightley",
                                                            "star_Kristen Stewart": "star_Kristen_Stewart",
                                                            "star_Leonardo DiCaprio": "star_Leonardo_DiCaprio",
                                                            "star_Marion Cotillard": "star_Marion_Cotillard",
                                                            "star_Mark Ruffalo": "star_Mark_Ruffalo",
                                                            "star_Matt Damon": "star_Matt_Damon",
                                                            "star_Robert Downey Jr.": "star_Robert_Downey_Jr_",
                                                            "star_Robert Pattinson": "star_Robert_Pattinson",
                                                            "star_Rupert Grint": "star_Rupert_Grint",
                                                            "star_Ryan Reynolds": "star_Ryan_Reynolds",
                                                            "star_Steve Carell": "star_Steve_Carell",
                                                            "star_Tom Cruise": "star_Tom_Cruise",
                                                            "star_Tom Hanks": "star_Tom_Hanks",
                                                            "star_Vin Diesel": "star_Vin_Diesel",
                                                            "star_Vincent Cassel": "star_Vincent_Cassel",
                                                            "star_Will Smith": "star_Will_Smith",
                                                            "star_Zoe Saldana": "star_Zoe_Saldana",
                                                            
                                                            "prod_Anthony Russo": "prod_Anthony_Russo",
                                                            "prod_Chris Morgan": "prod_Chris_Morgan",
                                                            "prod_Christopher Markus": "prod_Christopher_Markus",
                                                            "prod_Christopher Nolan": "prod_Christopher_Nolan",
                                                            "prod_Clint Eastwood": "prod_Clint_Eastwood",
                                                            "prod_Dany Boon": "prod_Dany_Boon",
                                                            "prod_David Koepp": "prod_David_Koepp",
                                                            "prod_David Yates": "prod_David_Yates",
                                                            "prod_Fabien Onteniente": "prod_Fabien_Onteniente",
                                                            "prod_Franck Dubosc": "prod_Franck_Dubosc",
                                                            "prod_Gore Verbinski": "prod_Gore_Verbinski",
                                                            "prod_Guillaume Canet": "prod_Guillaume_Canet",
                                                            "prod_J.J. Abrams": "prod_J_J__Abrams",
                                                            "prod_Jeff Nathanson": "prod_Jeff_Nathanson",
                                                            "prod_Joe Russo": "prod_Joe_Russo",
                                                            "prod_Jon Favreau": "prod_Jon_Favreau",
                                                            "prod_Jonathan Aibel": "prod_Jonathan_Aibel",
                                                            "prod_Luc Besson": "prod_Luc_Besson",
                                                            "prod_Melissa Rosenberg": "prod_Melissa_Rosenberg",
                                                            "prod_Neal Purvis": "prod_Neal_Purvis",
                                                            "prod_Olivier Baroux": "prod_Olivier_Baroux",
                                                            "prod_Peter Jackson": "prod_Peter_Jackson",
                                                            "prod_Philippa Boyens": "prod_Philippa_Boyens",
                                                            "prod_Philippe de Chauveron": "prod_Philippe_de_Chauveron",
                                                            "prod_Rick Jaffa": "prod_Rick_Jaffa",
                                                            "prod_Ridley Scott": "prod_Ridley_Scott",
                                                            "prod_Sam Raimi": "prod_Sam_Raimi",
                                                            "prod_Simon Kinberg": "prod_Simon_Kinberg",
                                                            "prod_Stephen McFeely": "prod_Stephen_McFeely",
                                                            "prod_Steve Kloves": "prod_Steve_Kloves",
                                                            "prod_Steven Spielberg": "prod_Steven_Spielberg",
                                                            "prod_Ted Elliott": "prod_Ted_Elliott",
                                                            "prod_Terry Rossio": "prod_Terry_Rossio",
                                                            "prod_Tim Burton": "prod_Tim_Burton"


                                                            })

        model_instance = model.load_model()
        predictions = model_instance.predict(cleaned_final_df)
        logger.info(f"Prediction complete for {len(csv_df)} movies")
        
        film_titles = cleaned_df['film_title'].tolist()
        predictions = predictions.tolist()

        response_data = {
            "Film titles": film_titles,
            "Predictions": predictions,
        }
        
        return response_data

    except Exception as e:
        logger.error(f"Error predicting from JSON: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"JSON prediction error: {str(e)}")
    
    ########################################################################################################

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)