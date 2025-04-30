
import datetime as dt
from ..models import PredictionHistory

def create_or_update_prediction(movie_id : int, first_week_predicted_entries_fr:int, prediction_error :int, model_version:int, date_prediction:dt.date) -> PredictionHistory:
    prediction_history = PredictionHistory.objects.filter(
        movie_id=movie_id
    ).first()

    if prediction_history :
        prediction_history.first_week_predicted_entries_france = first_week_predicted_entries_fr
        prediction_history.prediction_error = prediction_error
        prediction_history.model_version = model_version
        prediction_history.date = date_prediction
    else :
        prediction_history = PredictionHistory(
            movie_id = movie_id, 
            first_week_predicted_entries_france = first_week_predicted_entries_fr, 
            prediction_error = prediction_error,
            model_version = model_version,
            date = date_prediction
        )

    prediction_history.save()
    return prediction_history

def get_prediction_display_per_week(first_week_predicted_entries_france : int) -> float :
    value = float(first_week_predicted_entries_france)/2000.0
    return value

def get_prediction_display_per_day(first_week_predicted_entries_france : int) -> float :
    value = float(first_week_predicted_entries_france) / 14000.0
    return value

    
    