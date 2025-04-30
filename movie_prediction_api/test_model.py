# Enregistrez ceci comme analyze_model.py
from catboost import CatBoostRegressor
import pandas as pd
import numpy as np
import os

# Chemin absolu du modèle
model_path = "/home/l-o/Projets/film-prediction/movie_prediction_api/model/catboost_model.cbm"

print(f"Checking if model exists: {os.path.exists(model_path)}")
print(f"Model size: {os.path.getsize(model_path) if os.path.exists(model_path) else 'N/A'} bytes")

try:
    # Chargez le modèle
    model = CatBoostRegressor()
    model.load_model(model_path)
    print("Modèle chargé avec succès!")
    
    # Examinez les propriétés du modèle
    print("\nModèle properties:")
    
    # Feature names
    if hasattr(model, 'feature_names_'):
        feature_names = model.feature_names_
        print(f"Feature names: {feature_names}")
        print(f"Number of features: {len(feature_names)}")
    else:
        print("No feature names available")
    
    # Categorical features
    if hasattr(model, 'cat_features'):
        print(f"Categorical features: {model.cat_features}")
    else:
        print("No categorical features information available")
    
    # Test avec un tableau avec quelques features
    print("\nTesting prediction with some basic features:")
    # Créer un array de taille 1 x nombre de features
    n_features = len(model.feature_names_) if hasattr(model, 'feature_names_') else 10
    dummy_features = np.zeros((1, n_features))
    
    try:
        prediction = model.predict(dummy_features)
        print(f"Prediction successful: {prediction}")
    except Exception as pred_err:
        print(f"Prediction failed: {str(pred_err)}")
        
        # Essayons avec un DataFrame
        print("\nTrying with a DataFrame:")
        if hasattr(model, 'feature_names_'):
            df_features = pd.DataFrame(dummy_features, columns=model.feature_names_)
            try:
                prediction = model.predict(df_features)
                print(f"DataFrame prediction successful: {prediction}")
            except Exception as df_err:
                print(f"DataFrame prediction failed: {str(df_err)}")
    
    # Récupérer les informations de feature importance
    print("\nFeature importance (if available):")
    try:
        importances = model.get_feature_importance()
        if len(importances) > 0:
            # Créer un dictionnaire feature -> importance
            importance_dict = {}
            if hasattr(model, 'feature_names_'):
                for i, imp in enumerate(importances):
                    importance_dict[model.feature_names_[i]] = imp
            else:
                for i, imp in enumerate(importances):
                    importance_dict[f"Feature {i}"] = imp
            
            # Afficher les 10 features les plus importantes
            sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            for feature, importance in sorted_features[:10]:
                print(f"  {feature}: {importance}")
    except Exception as e:
        print(f"Could not get feature importance: {str(e)}")
    
except Exception as e:
    print(f"Error loading or analyzing model: {str(e)}")