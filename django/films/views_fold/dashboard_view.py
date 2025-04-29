import os
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Broadcast, Movie, PredictionHistory, INITIAL_DATE_FORMAT_STRING
from ..data_importer import DataImporter
from ..business.broadcast_utils import get_or_create_broadcast, get_start_wednesday, get_room_total_entries
from ..business.movie_list_utils import get_week_movies

import csv
import datetime as dt

from django.conf import settings
DATEPICKER_FORMAT_STRING = getattr(settings, "DATEPICKER_FORMAT_STRING", "%Y-%m-%d")

model_version = 0

def get_empty_movie(fake_release_date : dt.date) :
    empty_movie = Movie( 
        id=0,
        title ="image fixe",
        image_url = "",
        synopsis= "",
        genre = "",
        cast = "", 
        first_week_actual_entries_france = 0, 
        release_date_fr = fake_release_date)
    empty_movie.empty = True
    return empty_movie

#__________________________________________________________________________________________________
#
# region dashboard
#__________________________________________________________________________________________________
def dashboard(request):
    
    selected_day = dt.datetime.now()
    if request.method == "POST":
        # Récupérer la date envoyée par le formulaire
        selected_date_str = str(request.POST.get('selected_day'))
        selected_date_str = selected_date_str.split('T')[0]
        if selected_date_str:
            selected_day = dt.datetime.strptime(selected_date_str, DATEPICKER_FORMAT_STRING)
   

    start_wednesday = get_start_wednesday(selected_day.date())
    broadcast = get_or_create_broadcast(start_wednesday)
    room_1_movie = None
    if broadcast.room_1 :
        room_1_movie = Movie.objects.get(id= broadcast.room_1)
        if room_1_movie :
            room_1_movie.room = 1

    room_2_movie = None
    if broadcast.room_2 :
        room_2_movie = Movie.objects.get(id= broadcast.room_2)
        if room_2_movie :
            room_2_movie.room = 2

    current_week_broadcast_movies = []
    if room_1_movie :
        prediction_history = PredictionHistory.objects.filter(movie_id=room_1_movie.id).first()
        if prediction_history :
            room_1_movie.last_prediction = prediction_history.first_week_predicted_entries_france
            room_1_movie.room_total_entries = get_room_total_entries(broadcast, 1)

        current_week_broadcast_movies.append(room_1_movie)
    else :
        empty_movie= get_empty_movie(selected_day)
        empty_movie.room = 1
        current_week_broadcast_movies.append(empty_movie)

    if room_2_movie :
        prediction_history = PredictionHistory.objects.filter(movie_id=room_2_movie.id).first()
        if prediction_history :
            room_2_movie.last_prediction = prediction_history.first_week_predicted_entries_france
            room_2_movie.room_total_entries = get_room_total_entries(broadcast, 2)

        current_week_broadcast_movies.append(room_2_movie)
    else :
        empty_movie= get_empty_movie(selected_day)
        empty_movie.room = 2
        current_week_broadcast_movies.append(empty_movie)
    
    next_wednesday = start_wednesday + dt.timedelta(days=7)
    next_week_movies = get_week_movies(start_wednesday, next_wednesday)
    for movie in next_week_movies :
        prediction_history = PredictionHistory.objects.filter(movie_id=movie.id).first()
        if prediction_history :
            movie.last_prediction = prediction_history.first_week_predicted_entries_france
    
    context = {
        'selected_day' : selected_day,
        'selected_movies': current_week_broadcast_movies, 
        'upcoming_movies': next_week_movies,
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
