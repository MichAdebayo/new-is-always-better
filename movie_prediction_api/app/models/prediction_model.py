# prediction_model.py - Solution avec utilisation du modèle CatBoost
import os
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from catboost import CatBoostRegressor, Pool
import re
from sklearn.preprocessing import StandardScaler
# from app.preprocessing.feature_engineering import preprocess_movie_data


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MoviePredictionModel:
    def load_model(self, model_path: str = None):
        
        if model_path is None:
            model_path = "./model/catboost_model.cbm"

        logger.info(f"Model path: {model_path}")
        self.use_catboost = True  # Activation de l'utilisation de CatBoost

        try:
            # Charger le modèle CatBoost
            self.model = CatBoostRegressor()
            loaded_model = self.model.load_model(model_path)
            logger.info(f"Modèle CatBoost chargé avec succès depuis {model_path}")
            return loaded_model
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle CatBoost: {str(e)}")
            logger.info("Utilisation du modèle basé sur des règles comme solution de secours")
            self.use_catboost = False

    def create_list_based_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crée des colonnes de caractéristiques basées sur des listes à partir du DataFrame
        """

        """Create binary features for each top star"""
        if 'top_stars_list' not in df.columns:
            return df
        
        # List of stars from your data (can be expanded)
        stars = [
            'André Dussollier', 'Benoît Poelvoorde', 'Brad Pitt', 'Chris Evans',
            'Chris Pratt', 'Christian Clavier', 'Clovis Cornillac', 'Daniel Craig',
            'Daniel Radcliffe', 'Dany Boon', 'Dwayne Johnson', 'Emma Watson',
            'Ewan McGregor', 'Franck Dubosc', 'Gad Elmaleh', 'George Clooney',
            'Gilles Lellouche', 'Guillaume Canet', 'Gérard Depardieu', 'Gérard Lanvin',
            'Hugh Jackman', 'Isabelle Nanty', 'Jamel Debbouze', 'Jason Statham',
            'Jean Dujardin', 'Jean Reno', 'Jean-Paul Rouve', 'Johnny Depp',
            'José Garcia', 'Kad Merad', 'Keira Knightley', 'Kristen Stewart',
            'Leonardo DiCaprio', 'Marion Cotillard', 'Mark Ruffalo', 'Matt Damon',
            'Robert Downey Jr.', 'Robert Pattinson', 'Rupert Grint', 'Ryan Reynolds',
            'Steve Carell', 'Tom Cruise', 'Tom Hanks', 'Vin Diesel',
            'Vincent Cassel', 'Will Smith', 'Zoe Saldana'
        ]
    
        # Create features
        for star in stars:
            star_col = f'star_{star}'
            df[star_col] = df['top_stars_list'].apply(
                lambda x: 1 if isinstance(x, list) and star in x else 0
            )
        

        """Create binary features for each nationality"""
        if 'nationality_list' not in df.columns:
            return df
                
        # List of nationalities from your data
        nationalities = [
            'Allemagne', 'Australie', 'Belgique', 'Canada', 'Espagne', 
            'France', 'Grande-Bretagne', 'Italie', 'Japon', 
            'Nouvelle-Zélande', 'U.S.A.'
        ]
            
        # Create features
        for nat in nationalities:
            nat_col = f'nat_{nat}'
            df[nat_col] = df['nationality_list'].apply(
                lambda x: 1 if isinstance(x, list) and nat in x else 0
            )
            


        """Create binary features for each language"""
        if 'languages_list' not in df.columns:
            return df
                
        # List of languages from your data
        languages = [
            'ARABIC', 'Allemand', 'Anglais', 'Chinois', 'Espagnol', 
            'Français', 'Hébreu', 'Italien', 'Japonais', 'Latin',
            'Mandarin', 'Portugais', 'Russe'
        ]
        
        # Create features
        for lang in languages:
            lang_col = f'lang_{lang}'
            df[lang_col] = df['languages_list'].apply(
                lambda x: 1 if isinstance(x, list) and lang in x else 0
            )
            

        """Create binary features for each producer"""
        if 'producers_list' not in df.columns:
            return df
                
        # List of producers from your data
        producers = [
            'Anthony Russo', 'Chris Morgan', 'Christopher Markus', 'Christopher Nolan',
            'Clint Eastwood', 'Dany Boon', 'David Koepp', 'David Yates',
            'Fabien Onteniente', 'Franck Dubosc', 'Gore Verbinski', 'Guillaume Canet',
            'J.J. Abrams', 'Jeff Nathanson', 'Joe Russo', 'Jon Favreau',
            'Jonathan Aibel', 'Luc Besson', 'Melissa Rosenberg', 'Neal Purvis',
            'Olivier Baroux', 'Peter Jackson', 'Philippa Boyens', 'Philippe de Chauveron',
            'Rick Jaffa', 'Ridley Scott', 'Sam Raimi', 'Simon Kinberg',
            'Stephen McFeely', 'Steve Kloves', 'Steven Spielberg', 'Ted Elliott',
            'Terry Rossio', 'Tim Burton'
        ]
        
        # Create features
        for prod in producers:
            prod_col = f'prod_{prod}'
            df[prod_col] = df['producers_list'].apply(
                lambda x: 1 if isinstance(x, list) and prod in x else 0
            )

        return df
    
    def create_data_for_prediction(self, movie_data: pd.DataFrame) -> pd.DataFrame:

        data_for_prediction = movie_data[[
                "duration",
                "synopsis_length",
                "award_count",
                "nomination_count",
                "trailer_views_num",
                "filming_secrets_num",
                "top_distributor_score",
                "distributor_power",
                "franchise_blockbuster_score",
                "estimated_marketing_power",
                "year_of_production",
                "release_date_france_year",
                "release_date_france_day",
                "release_season",
                "broadcast_category",
                "duration_binary",
                "director_binary",
                "producers_count_binary",
                "top_stars_count_binary",
                "press_rating_binary",
                "nationality_list_binary",
                "viewer_rating_binary",
                "trailer_views_num_binary",
                "synopsis_binary",
                "distributor_binary",
                "duration_classified",
                "synopsis_sentiment",
                "is_sequel",
                "synopsis_length_categorized",
                "synopisis_sentiment_categorized",
                "award_binary",
                "nomination_binary",
                "is_gaming_franchise",
                "franchise_level",
                "is_superhero_franchise",
                "is_animation_franchise",
                "is_action_franchise",
                "is_licence",
                "is_mcu",
                "is_likely_blockbuster",
                "is_major_studio",
                "is_french_major_studio",
                "major_studio_and_licence",
                "french_major_and_licence",
                "major_studio_x_franchise",
                "is_connected_universe",
                "film_title",
                "director",
                "distributor",
                "lang_ARABIC",
                "lang_Allemand",
                "lang_Anglais",
                "lang_Chinois",
                "lang_Espagnol",
                "lang_Français",
                "lang_Hébreu",
                "lang_Italien",
                "lang_Japonais",
                "lang_Latin",
                "lang_Mandarin",
                "lang_Portugais",
                "lang_Russe",
                "nat_Allemagne",
                "nat_Australie",
                "nat_Belgique",
                "nat_Canada",
                "nat_Espagne",
                "nat_France",
                "nat_Grande-Bretagne",
                "nat_Italie",
                "nat_Japon",
                "nat_Nouvelle-Zélande",
                "nat_U.S.A.",
                "star_André Dussollier",
                "star_Benoît Poelvoorde",
                "star_Brad Pitt",
                "star_Chris Evans",
                "star_Chris Pratt",
                "star_Christian Clavier",
                "star_Clovis Cornillac",
                "star_Daniel Craig",
                "star_Daniel Radcliffe",
                "star_Dany Boon",
                "star_Dwayne Johnson",
                "star_Emma Watson",
                "star_Ewan McGregor",
                "star_Franck Dubosc",
                "star_Gad Elmaleh",
                "star_George Clooney",
                "star_Gilles Lellouche",
                "star_Guillaume Canet",
                "star_Gérard Depardieu",
                "star_Gérard Lanvin",
                "star_Hugh Jackman",
                "star_Isabelle Nanty",
                "star_Jamel Debbouze",
                "star_Jason Statham",
                "star_Jean Dujardin",
                "star_Jean Reno",
                "star_Jean-Paul Rouve",
                "star_Johnny Depp",
                "star_José Garcia",
                "star_Kad Merad",
                "star_Keira Knightley",
                "star_Kristen Stewart",
                "star_Leonardo DiCaprio",
                "star_Marion Cotillard",
                "star_Mark Ruffalo",
                "star_Matt Damon",
                "star_Robert Downey Jr.",
                "star_Robert Pattinson",
                "star_Rupert Grint",
                "star_Ryan Reynolds",
                "star_Steve Carell",
                "star_Tom Cruise",
                "star_Tom Hanks",
                "star_Vin Diesel",
                "star_Vincent Cassel",
                "star_Will Smith",
                "star_Zoe Saldana",
                "prod_Anthony Russo",
                "prod_Chris Morgan",
                "prod_Christopher Markus",
                "prod_Christopher Nolan",
                "prod_Clint Eastwood",
                "prod_Dany Boon",
                "prod_David Koepp",
                "prod_David Yates",
                "prod_Fabien Onteniente",
                "prod_Franck Dubosc",
                "prod_Gore Verbinski",
                "prod_Guillaume Canet",
                "prod_J.J. Abrams",
                "prod_Jeff Nathanson",
                "prod_Joe Russo",
                "prod_Jon Favreau",
                "prod_Jonathan Aibel",
                "prod_Luc Besson",
                "prod_Melissa Rosenberg",
                "prod_Neal Purvis",
                "prod_Olivier Baroux",
                "prod_Peter Jackson",
                "prod_Philippa Boyens",
                "prod_Philippe de Chauveron",
                "prod_Rick Jaffa",
                "prod_Ridley Scott",
                "prod_Sam Raimi",
                "prod_Simon Kinberg",
                "prod_Stephen McFeely",
                "prod_Steve Kloves",
                "prod_Steven Spielberg",
                "prod_Ted Elliott",
                "prod_Terry Rossio",
                "prod_Tim Burton"
            ]].copy()

        return data_for_prediction
    
    def _preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prétraite le DataFrame pour éliminer les structures problématiques
        et standardize les colonnes numériques
        """
        # Créer une copie pour éviter de modifier l'original
        cleaned_df = df.copy()
        
         # Standard scaling pour les colonnes numériques importantes
         # en s'inspirant du notebook
        numeric_cols = [
             'duration', 'synopsis_length', 'award_count', 'nomination_count',
            'trailer_views_num', 'filming_secrets_num', 'top_distributor_score',             'distributor_power', 'franchise_blockbuster_score', 'estimated_marketing_power'
         ]
       
         # Vérifier quelles colonnes sont disponibles
        available_numeric_cols = [col for col in numeric_cols if col in cleaned_df.columns]
        
        if available_numeric_cols:
             # Appliquer standard scaling comme dans le notebook
            scaler = StandardScaler()
            try:
                 # Convertir les colonnes en float pour éviter les problèmes
                for col in available_numeric_cols:
                     cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce').fillna(0)
                
                 # Appliquer le scaling
                cleaned_df[available_numeric_cols] = scaler.fit_transform(cleaned_df[available_numeric_cols])
                logger.info(f"Applied standard scaling to {len(available_numeric_cols)} numeric columns")
            except Exception as e:
                logger.warning(f"Error during standard scaling: {str(e)}")
        
        categorical_cols = [ 
             'year_of_production', 'release_date_france_year', 'release_date_france_day',
             'release_season', 
             'broadcast_category', 
             'duration_binary',
             'director_binary',
             'producers_count_binary', 'top_stars_count_binary',
             'press_rating_binary', 'nationality_list_binary', 
             'viewer_rating_binary', 'trailer_views_num_binary',
             'synopsis_binary', 'distributor_binary',
             'duration_classified', 'synopsis_sentiment', 'is_sequel',
             'synopsis_length_categorized', 'synopisis_sentiment_categorized',
             'award_binary', 'nomination_binary','is_gaming_franchise',
             'franchise_level', 'is_superhero_franchise',
             'is_animation_franchise', 'is_action_franchise',
             'is_licence',  'is_mcu', 'is_likely_blockbuster',
             'is_major_studio', 'is_french_major_studio', 'major_studio_and_licence',
             'french_major_and_licence', 'major_studio_x_franchise', 'is_connected_universe',]
        
        cleaned_df[categorical_cols] = cleaned_df[categorical_cols].apply(lambda x: x.astype(str).astype('category'))
        
        object_cols = ["director", "distributor"]
        cleaned_df[object_cols] = cleaned_df[object_cols].apply(lambda x: x.astype(str).astype('category'))


        return cleaned_df
    
    
#     def predict(self, features: pd.DataFrame) -> List[Dict[str, Any]]:
#         """
#         Make predictions for movie entries
#         """
#         # Log information about the features
#         logger.info(f"Predicting for {len(features)} movies")
#         logger.info(f"Columns used for prediction: {features.columns.tolist()}")
#         # # Nettoyage et préparation des données
#         # cleaned_features = self._preprocess_dataframe(features)
        
#         if self.use_catboost:
#             try:
#                 # Préparation finale des données pour le modèle CatBoost
#                 new_prediction = self.model.predict(features)
#                 return new_prediction.tolist()  # Assurez-vous que le retour est une liste
#             except Exception as e:
#                 logger.error(f"Error during CatBoost prediction: {str(e)}")
#                 logger.info("Issue with prediction")
#                 return []  # Retourner une liste vide en cas d'erreur
#         else:
#             # Utiliser le modèle basé sur des règles si CatBoost n'est pas disponible
#             logger.info("CatBoost model not available, returning empty predictions")
#             return []  # Retourner une liste vide ou implémenter une solution de secours

# if __name__ == "__main__":
#     # Create an instance of the MoviePredictionModel
#     model = MoviePredictionModel()

#     # Step 1: Preprocess the raw data
#     raw_df = preprocess_movie_data()

#     print(raw_df.columns.tolist())

#     # Step 2: Filter the data for prediction
#     filtered_df = model.create_data_for_prediction(raw_df)
#     print(filtered_df.columns.tolist())

# #     # Step 3: Preprocess the filtered data
# #     cleaned_df = model._preprocess_dataframe(filtered_df)

# #     # Step 4: Make predictions
# #     predictions = model.predict(cleaned_df)

# #     # Log or print the predictions
# #     logger.info(f"Predictions: {predictions}")

        # # Create results
        # results = []
        # for i, film_title in enumerate(features['film_title']):
        #     result = {
        #         'film_title': film_title,
        #         'predicted_fr_entries': predictions[i],
        #         'features': {'method': prediction_method}  # Afficher la méthode réellement utilisée
            # }
            # results.append(result)

    
    # def _postprocess_predictions(self, raw_predictions, features):
    #     """
    #     Applique un post-traitement universel aux prédictions brutes
    #     pour les ramener à une échelle réaliste sans référence à des films spécifiques
    #     """
    #     # Vérifier si nous avons des prédictions anormalement élevées
    #     max_pred = np.max(raw_predictions)
        
    #     # Si les prédictions semblent trop élevées (au-delà de ce qui est réaliste)
    #     if max_pred > 4000000:  # Seuil déterminé empiriquement pour le marché français
    #         logger.info(f"Detected unusually high predictions (max: {max_pred}), applying scaling")
            
    #         # Appliquer une fonction de calibration non-linéaire 
    #         # qui préserve les valeurs basses mais compresse les valeurs élevées
    #         # Paramètres déterminés empiriquement
    #         scaling_factor = 4000000 / max_pred  # Ajuste le max à 4M (plafond réaliste)
            
    #         # Transformation non-linéaire qui préserve mieux l'ordre relatif
    #         calibrated = []
    #         for pred in raw_predictions:
    #             if pred <= 1000000:  # Petits et moyens films intacts
    #                 calibrated.append(pred)
    #             else:  # Blockbusters compressés progressivement
    #                 # Fonction racine qui atténue les grandes valeurs
    #                 scaled = 1000000 + (pred - 1000000) * scaling_factor
    #                 calibrated.append(scaled)
                    
    #         logger.info(f"Scaling applied: max raw={max_pred}, max calibrated={max(calibrated)}")
    #         return calibrated
    #     else:
    #         # Si les prédictions semblent raisonnables, les laisser telles quelles
    #         logger.info(f"Predictions seem reasonable (max: {max_pred}), no scaling needed")
    #         return raw_predictions
            

    
   

# Get or create the model instance
# def get_model_instance(model_path: str = None) -> MoviePredictionModel:
#     """Get or create the model instance"""
#     return MoviePredictionModel(model_path)