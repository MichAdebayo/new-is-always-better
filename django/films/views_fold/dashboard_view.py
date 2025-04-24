import os
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Movie, PredictionHistory, INITIAL_DATE_FORMAT_STRING
from ..data_importer import DataImporter

import csv
import datetime as dt


model_version = 0

#__________________________________________________________________________________________________
#
# region dashboard
#__________________________________________________________________________________________________
def dashboard(request):
    
    today = dt.datetime.now()
    limit_date =  today - dt.timedelta(days=30)

    recent_movies = Movie.objects.filter(  
            release_date_fr__gt = limit_date
        ).order_by(
            '-release_date_fr'
        ).prefetch_related('predictions').all()

    for movie in recent_movies :
        predictions = movie.predictions.all()
        if len(predictions) >0 :
            movie.last_prediction = predictions.last().first_week_predicted_entries_france

    selected_movies = recent_movies[:2]
    upcoming_movies = recent_movies[2:] 
    
    context = {
        'selected_movies': selected_movies, 
        'upcoming_movies': upcoming_movies,
        'active_tab': 'dashboard'
    }

    return render(request, 'films/dashboard.html', context)

#__________________________________________________________________________________________________
#
# region run_movie_prediction
#__________________________________________________________________________________________________
def run_movie_prediction(request, movie_id) :
    movie = get_object_or_404(Movie, id=movie_id)

    from first_predictor import FirstPredictor
    predictor = FirstPredictor(model_version)
    (prediction, error) = predictor.predict(movie.title, "")
    
    import datetime as dt
    today = dt.datetime.now().date()

    new_entry = PredictionHistory(
        movie_id = movie.id, 
        first_week_predicted_entries_france = prediction, 
        prediction_error = error,
        model_version = predictor.model_version,
        date = today
    )
    new_entry.save()

    messages.success(request, f"Action launched for the movie: {movie.title}")
    return redirect('dashboard')  
